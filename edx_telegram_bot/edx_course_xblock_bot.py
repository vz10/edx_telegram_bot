# -*- coding: utf-8 -*-
import time
import telegram
import random
import json
import pymongo
from bs4 import BeautifulSoup
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, CallbackQueryHandler
from django.contrib.sites.models import Site
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.content import StaticContent
from openedx.core.djangoapps.credit.utils import get_course_blocks
from opaque_keys.edx.keys import UsageKey
from student.models import anonymous_id_for_user
from submissions import api

from models import (EdxTelegramUser, UserCourseProgress, BotFriendlyCourses, TelegramBot)
from decorators import is_telegram_user
from bot_mongo import BotMongo


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


bot_messages = {
    'help_now': "I know the right answer",
    'not_know': "I need to read a bit of theory",
    'now_i_can': "Now I'm ready to answer",
    'next_theory': "Next theoretical part",
    'next_question': "Next question",
    'next_theme': "Next theme",
    'finish': 'The course is finished, there is no one at home, come later.',
    'hi': "Hi Earthman! I'm glad to see you",
    'correct_answer': "Great answer, you've got %d points fot that question",
    'incorrect_answer': 'Incorrect answer :('
}


content_method = {'video': 'sendVideo',
                  'paragraph': 'sendMessage',
                  'image': 'sendPhoto'}


class CourseBot(object):
    def __init__(self, **kwargs):
        """
        add commands and start bot
        :return:
        """

        self.category = 'bot_xblock'

        self.commands = {
            '/hi': 'Try it if you want to say hi to the Bot',
            '/restart': 'Restart current course',
            'nothing more...': 'For more talking use keyboard in course '
            # '/courses': 'You can choose what kind of courses you are interesting in',
            # '/all_courses': "You can see all available courses",
            # '/my_courses': "You can see only your courses",
            # '/recommendations': "You can ask bot to recommend you some courses which will be interesting for you",
            # '/reminder': "In 30 seconds bot will remind you that you are idiot",
            # '/die': "Don't even think about it, motherfucker"
        }

        self.token = kwargs.get('token', 'course_name')
        self.telegram_bot = TelegramBot.objects.get(token=self.token)
        self.updater = Updater(token=self.token, workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addHandler(CommandHandler('hi', self.hi))
        self.dispatcher.addHandler(CommandHandler('help', self.help_command))
        self.dispatcher.addHandler(CommandHandler('start', self.start))
        self.dispatcher.addHandler(CommandHandler('restart', self.restart))
        self.dispatcher.addHandler(MessageHandler([Filters.text], self.echo))
        self.dispatcher.addHandler(CallbackQueryHandler(self.inline_keyboard))
        # self.dispatcher.addHandler(CommandHandler('die', self.die))
        # self.dispatcher.addHandler(CommandHandler('reminder', self.reminder))
        self.dispatcher.addErrorHandler(self.error)
        self.dispatcher.addHandler(RegexHandler(r'/.*', self.unknown))
        self.mongo_client = BotMongo(database='bot', collection='messages')
        self.check_or_create_mongo_index()
        self.queue = self.updater.start_polling()

    def check_or_create_mongo_index(self):
        print self.mongo_client.check_index()
        if 'message_id_1_chat_id_1' not in self.mongo_client.check_index():
            print self.mongo_client.set_index([('message_id', pymongo.ASCENDING),('chat_id',pymongo.ASCENDING)])
            import pdb; pdb.set_trace()

    @property
    def course_key(self):
        try:
            return BotFriendlyCourses.objects.filter(bot=self.telegram_bot).first().course_key
        except AttributeError:
            return None

    def sendMessage(self, bot, chat_id, 
                    content='', content_type='paragraph', 
                    keyboard_dict=None, parse_mode=telegram.ParseMode.HTML):
        reply_markup = None
        if self.course_key:
            if keyboard_dict:
                keyboard = map(lambda item: [InlineKeyboardButton(text=keyboard_dict[item]['text'],
                                                                  callback_data=json.dumps({'key_id':item}))],
                               keyboard_dict)
                reply_markup = InlineKeyboardMarkup(keyboard)
            msg = getattr(bot, content_method[content_type])(chat_id, 
                                                             content, 
                                                             reply_markup=reply_markup,
                                                             parse_mode=parse_mode)
            self.mongo_client.send({'message_id': msg.message_id,
                                    'chat_id': chat_id,
                                    'text': content,
                                    'keyboard': keyboard_dict})
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="I'm not connected to any course right now",
                            parse_mode=parse_mode)

    def get_xblock_for_step(self, step, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        if progress.xblock_key:
            usage_key = UsageKey.from_string(progress.xblock_key)
            xblock = modulestore().get_item(usage_key)
            return xblock
        else:
            # course_key = CourseKey.from_string(self.course_key)
            # bot_xblocks = get_course_blocks(course_key, self.category)

            bot_xblocks = []
            course_key = CourseKey.from_string(self.course_key)
            course = modulestore().get_course(course_key)
            for sequence in course.get_children():
                for units in sequence.get_children():
                    for verticals in units.get_children():
                        for xblocks in verticals.get_children():
                            if xblocks.category == self.category:
                                bot_xblocks.append(xblocks)
            if step > len(bot_xblocks) - 1:
                progress.current_step_status = UserCourseProgress.STATUS_END
                progress.save()
                return
            else:
                progress.xblock_key = str(bot_xblocks[step].location)
                progress.save()
                return bot_xblocks[step]

    @staticmethod
    def get_block_title(container):
        return container.display_name

    def get_html_for_block(self, container, html_block_number):
        output = []
        xblock = container.get_children()[html_block_number]
        if xblock.category == 'html':
            data = xblock.data
            soup = BeautifulSoup(data, 'html.parser')
            for each in soup.find_all('p'):
                if each.find('img'):
                    validate = URLValidator()
                    url = each.find('img').get('src')
                    try:
                        validate(url)
                    except ValidationError:
                        current_domen = Site.objects.get_current()
                        course_key = CourseKey.from_string(self.course_key)
                        url = '%s%s%s' % (current_domen,
                                          StaticContent.get_base_url_path_for_course_assets(course_key),
                                          url[8:])
                    output.append({'type': 'image',
                                   'content': url})
                else:
                    output.append({'type': 'paragraph',
                                   'content': each.get_text()})
        elif xblock.category == 'video':
            current_domen = Site.objects.get_current()
            course_key = CourseKey.from_string(self.course_key)
            start_url = '%s%s' % (current_domen, StaticContent.get_base_url_path_for_course_assets(course_key))
            for each in xblock.html5_sources:
                output.append({'type': 'video',
                               'content': start_url + each[8:]})
        return output

    def get_positive_message(self, container):
        return self.get_html_for_block(container, container.theoretical_part + container.question_part)

    def get_negative_message(self, container):
        return self.get_html_for_block(container,
                                       container.theoretical_part +
                                       container.question_part +
                                       container.positive_part)

    def send_message_from_html_dict(self, bot, chat_id, message, keyboard_dict):
        # if message['type'] == 'paragraph':
        #     self.sendMessage(bot,
        #                      chat_id=chat_id,
        #                      text=message['content'],
        #                      keyboard_dict=keyboard_dict)
        # elif message['type'] == 'image':
        #     self.sendPhoto(bot,
        #                   chat_id=chat_id,
        #                   photo=message['content'].encode('utf-8', 'strict'),
        #                   keyboard_dict=keyboard_dict)
        # elif message['type'] == 'video':
        #     self.sendVideo(bot,
        #                   chat_id=chat_id,
        #                   video=message['content'].encode('utf-8', 'strict'),
        #                   keyboard_dict=keyboard_dict)

        self.sendMessage(bot, 
                         chat_id=chat_id,
                         content=message['content'].encode('utf-8', 'strict'),
                         content_type=message['type'],
                         keyboard_dict=keyboard_dict)

    def output_non_question_xblock(self, bot, chat_id, message_dict, final_message, params_dict):
        keyboard_dict = None
        for count, each in enumerate(message_dict):
            if count == len(message_dict) - 1:
                keyboard_dict = {'0': {'text': final_message,
                                       'callback_data': params_dict}}     
            self.send_message_from_html_dict(bot, chat_id, each, keyboard_dict)

    @staticmethod
    def get_question_for_block(container, question_block_numpber):
        data = container.get_children()[container.theoretical_part + question_block_numpber].data
        soup = BeautifulSoup(data, 'html.parser')
        wrong_answers = [each.get_text() for each in soup.find_all(correct="false")]
        right_answer = [each.get_text() for each in soup.find_all(correct="true")]
        weight = container.get_children()[container.theoretical_part + question_block_numpber].weight
        if weight is None:
            weight = 1
        soup.multiplechoiceresponse.extract()
        question = soup.problem.get_text()
        return question, wrong_answers, right_answer, weight

    def hi(self, bot, update):
        print (update)
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        self.sendMessage(bot, chat_id=chat_id, content=bot_messages['hi'])
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')

    def unknown(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = """
                    Sorry, bro. I'm just a little raccoon and I don't know such words.
                    Maybe you'll try /help page to improve our communication?
                  """
        self.sendMessage(bot,
                         chat_id=chat_id,
                         content=message)

    @is_telegram_user
    def start(self, bot, update):
        chat_id = update.message.chat_id
        self.sendMessage(bot=bot,
                         chat_id=chat_id,
                         content="Hi, let's start out course")
        if self.course_key:
            telegram_id = update.message.from_user.id
            telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
            UserCourseProgress.objects.get_or_create(telegram_user=telegram_user, course_key=self.course_key)
            self.show_progress(bot, chat_id, telegram_user)

    @is_telegram_user
    def restart(self, bot, update):
        chat_id = update.message.chat_id
        self.sendMessage(bot=bot, chat_id=chat_id,
                         content="Let's start from scratch")
        if self.course_key:
            telegram_id = update.message.from_user.id
            telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
            UserCourseProgress.objects.filter(telegram_user=telegram_user, course_key=self.course_key).delete()
            UserCourseProgress.objects.create(telegram_user=telegram_user, course_key=self.course_key)
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
            self.show_progress(bot, chat_id, telegram_user)

    def help_command(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        self.sendMessage(bot,
                         chat_id=chat_id,
                         content="I have a lot of raccoon-workers, all of them want to help you, but they not"
                              " very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            self.sendMessage(bot, chat_id=chat_id, content=command + ' - ' + description)

    def not_know(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        progress.current_step_status = UserCourseProgress.STATUS_INFO
        progress.grade_for_step = 0
        progress.block_in_status = 0
        progress.save()
        self.show_progress(bot, chat_id, telegram_user)

    def ready(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        progress.current_step_status = UserCourseProgress.STATUS_TEST
        progress.grade_for_step = 0
        progress.block_in_status = 0
        progress.save()
        self.show_progress(bot, chat_id, telegram_user)

    def grade_xblock(self, container, step, grade, telegram_user):
        xblock = container.get_children()[container.theoretical_part + step]
        submission_id = {"item_id": xblock.location,
                         "item_type": 'bot_xblock',
                         "course_id": container.course_id,
                         "student_id": anonymous_id_for_user(telegram_user.student, container.course_id)}
        submission = api.create_submission(submission_id, {'comment': 'from bot'}, attempt_number=1)
        api.set_score(submission['uuid'], int(grade), int(xblock.weight or 1))

    def check(self, bot, chat_id, telegram_user, weight=1):
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        # Grade current questional Xblock
        current_step = self.get_xblock_for_step(progress.current_step_order, telegram_user)
        self.grade_xblock(current_step, progress.block_in_status, weight, telegram_user)
        print weight
        message = bot_messages['incorrect_answer'] if weight == 0 else bot_messages['correct_answer'] % int(weight)
        progress.grade_for_step += weight
        progress.block_in_status += 1
        # Check passing grade if it was the last question in Xblock
        if progress.block_in_status == current_step.question_part:
            self.sendMessage(bot, chat_id=chat_id, content=message)
            if progress.grade_for_step >= current_step.passing_grade:
                course_key = CourseKey.from_string(self.course_key)
                bot_xblocks_count = len(get_course_blocks(course_key, self.category))
                if progress.current_step_order < bot_xblocks_count - 1:
                    message_dict = self.get_positive_message(current_step)
                    self.output_non_question_xblock(bot,
                                                    chat_id,
                                                    message_dict,
                                                    bot_messages['next_theme'],
                                                    {'method': 'show_progress',
                                                     'kwargs': {}})
                    progress.grade_for_step = 0
                    progress.block_in_status = 0
                    progress.current_step_order += 1
                    progress.xblock_key = None
                    progress.current_step_status = UserCourseProgress.STATUS_START
                else:
                    message = "You've completed this course"
                    self.sendMessage(bot, chat_id=chat_id, content=message)
                    progress.current_step_status = UserCourseProgress.STATUS_END

            else:
                message_dict = self.get_negative_message(current_step)
                self.output_non_question_xblock(bot,
                                                chat_id,
                                                message_dict,
                                                bot_messages['not_know'],
                                                {'method': 'not_know',
                                                 'kwargs': {}})
        else:
            keyboard_dict = {'0':{'text': bot_messages['next_question'],
                                  'callback_data': {'method': 'show_progress',
                                                    'kwargs': {}}}}
            self.sendMessage(bot,
                             chat_id=chat_id,
                             content=message,
                             keyboard_dict=keyboard_dict)
        progress.save()

    def inline_keyboard(self, bot, update):
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id)
        message = self.mongo_client.find_one({'message_id': message_id, 'chat_id': chat_id})

        if self.course_key:
            answer = json.loads(update.callback_query.data)         
            self.sendMessage(bot, chat_id, message['keyboard'][answer['key_id']]['text'])
            method = message['keyboard'][answer['key_id']]['callback_data']['method']
            kwargs = message['keyboard'][answer['key_id']]['callback_data']['kwargs']
            telegram_id = update.callback_query.from_user.id
            telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
            getattr(self, method)(bot, chat_id, telegram_user, **kwargs)
        else:
            self.sendMessage(bot, chat_id)

    def show_progress(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.get_xblock_for_step(progress.current_step_order, telegram_user)
        if progress.current_step_status == UserCourseProgress.STATUS_START:
            keyboard_dict = {'0': {'text': bot_messages['help_now'],
                                   'callback_data': {'method': 'ready', 'kwargs': {}}},
                             '1': {'text': bot_messages['not_know'],
                                   'callback_data': {'method': 'not_know', 'kwargs': {}}}}
            message = self.get_block_title(current_step)
            self.sendMessage(bot,
                             chat_id=chat_id,
                             content=message,
                             keyboard_dict=keyboard_dict)
        if progress.current_step_status == UserCourseProgress.STATUS_TEST:
            question, wrong_answers, right_answer, weight = self.get_question_for_block(current_step,
                                                                                        progress.block_in_status)
            keyboard_dict = {str(num): {'text': each,
                                        'callback_data': {'method': 'check',
                                                          'kwargs': {'weight': 0}}}
                            for num, each in enumerate(wrong_answers)}
            keyboard_dict['right'] = {'text': right_answer[0],
                                      'callback_data': {'method': 'check',
                                                        'kwargs': {'weight': weight}}}
            message = question
            self.sendMessage(bot,
                             chat_id=chat_id,
                             content=message,
                             keyboard_dict=keyboard_dict)
        if progress.current_step_status == UserCourseProgress.STATUS_INFO:
            message_dict = self.get_html_for_block(current_step, progress.block_in_status)
            progress.block_in_status += 1
            progress.save()
            if progress.block_in_status == current_step.theoretical_part:
                final_message = bot_messages['now_i_can']
                params_dict = {'method': 'ready', 'kwargs': {}}
            else:
                final_message = bot_messages['next_theory']
                params_dict = {'method': 'show_progress', 'kwargs': {}}
            self.output_non_question_xblock(bot, chat_id,
                                            message_dict,
                                            final_message,
                                            params_dict)
            # if 'Video_url' in current_step:
            #     bot.sendVideo(chat_id=chat_id, video=current_step['Video_url'].encode('utf-8', 'strict'))
            # elif 'Image_url' in current_step:
            #     bot.sendPhoto(chat_id=chat_id, photo=current_step['Image_url'].encode('utf-8', 'strict'))

    def echo(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        try:
            progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
            if progress.current_step_status == UserCourseProgress.STATUS_END:
                self.sendMessage(bot,
                                 chat_id=chat_id,
                                 content=bot_messages['finish'])
                return
        except Exception as e:
            print e;
        self.unknown(bot, update)

    def die(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        self.sendMessage(bot, chat_id=chat_id, content='AAAAAAAA!!!! You kill me, motherfucker')
        self.sendMessage(bot, chat_id=chat_id, content="But I'll be back!!!!")
        self.updater.stop()

    @staticmethod
    def error(bot, update, error):
        print 'Update %s caused error %s' % (update, error)

    def reminder(self, bot, update):
        print 'reminder'
        chat_id = update.message.chat_id

        def job(bot):
            self.sendMessage(bot, chat_id=chat_id, content='30 seconds passed and I want to'
                                                        ' remind you that you are fucking idiot')

        self.j.put(job, 30, repeat=False)


print "start course bot"
