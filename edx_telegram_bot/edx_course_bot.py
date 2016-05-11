# -*- coding: utf-8 -*-
import time
import telegram
import random
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, CallbackQueryHandler

from bot_mongo import BotMongo

from models import (EdxTelegramUser, UserCourseProgress)
from decorators import is_telegram_user, close_connection



import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


bot_messages = {
    'help_now': "I know the right answer",
    'not_know': "I need to read a bit of theory",
    'now_i_can': "Now I'm ready to answer",
    'finish': 'The course is finished, there is no one at home, come later.',
    'hi': "Hi Earthman! I'm glad to see you"
}


class CourseBot(object):
    def __init__(self, **kwargs):
        """
        add commands and start bot
        :return:
        """

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

        self.updater = Updater(token=kwargs.get('token', 'course_name'), workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addHandler(CommandHandler('hi', self.hi))
        self.dispatcher.addHandler(CommandHandler('help', self.help_command))
        self.dispatcher.addHandler(CommandHandler('start', self.start))
        self.dispatcher.addHandler(CommandHandler('restart', self.restart))
        self.dispatcher.addHandler(MessageHandler([Filters.text],self.echo))
        self.dispatcher.addHandler(CallbackQueryHandler(self.inline_keyboard))
        # self.dispatcher.addHandler(CommandHandler('die', self.die))
        # self.dispatcher.addHandler(CommandHandler('reminder', self.reminder))


        self.dispatcher.addErrorHandler(self.error)
        self.dispatcher.addHandler(RegexHandler(r'/.*', self.unknown))

        self.queue = self.updater.start_polling()

        self.course_key = kwargs.get('collection', 'course_name')
        self.mongo_client = BotMongo(database='bot', collection=self.course_key)

    def help_command(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        bot.sendMessage(chat_id=chat_id,
                        text="I have a lot of raccoon-workers, all of them want to help you, but they not" \
                             " very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)

    @close_connection
    @is_telegram_user
    def start(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        UserCourseProgress.objects.get_or_create(telegram_user=telegram_user, course_key=self.course_key)
        self.show_progress(bot, chat_id, telegram_user)

    @close_connection
    @is_telegram_user
    def restart(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress = UserCourseProgress.objects.get_or_create(telegram_user=telegram_user, course_key=self.course_key)[0]
        progress.current_step_order = 0
        progress.current_step_status = UserCourseProgress.STATUS_TEST
        progress.save()
        bot.sendMessage(chat_id=chat_id,
                        text="Let's start from scratch")
        self.show_progress(bot, chat_id, telegram_user)

    @close_connection
    def not_know(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        progress.current_step_status = UserCourseProgress.STATUS_INFO
        progress.save()
        self.show_progress(bot, chat_id, telegram_user)

    @close_connection
    def ready(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        progress.current_step_status = UserCourseProgress.STATUS_TEST
        progress.save()
        self.show_progress(bot, chat_id, telegram_user)

    @close_connection
    def right(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.mongo_client.find_one({'Order': progress.current_step_order})
        bot.sendMessage(chat_id=chat_id,
                        text=current_step['Positive_answer'],
                        parse_mode=telegram.ParseMode.MARKDOWN)
        try:
            progress.current_step_status = UserCourseProgress.STATUS_START
            progress.current_step_order = current_step['Next_step_order']
            progress.save()
        except KeyError:
            progress.current_step_status = UserCourseProgress.STATUS_END
            progress.save()
            return
        self.show_progress(bot, chat_id, telegram_user)

    @close_connection
    def wrong(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.mongo_client.find_one({'Order': progress.current_step_order})
        not_know_button = InlineKeyboardButton(text=bot_messages['not_know'],
                                               callback_data='not_know')
        reply_markup = InlineKeyboardMarkup([[not_know_button]])
        bot.sendMessage(chat_id=chat_id,
                        text=current_step['Negative_answer'],
                        reply_markup=reply_markup,
                        parse_mode=telegram.ParseMode.MARKDOWN)

    def inline_keyboard(self, bot, update):
        answer = update.callback_query.data
        telegram_id = update.callback_query.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        text = update.callback_query.message.text

        bot.editMessageText(chat_id=chat_id, message_id=message_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        getattr(self, answer)(bot, chat_id, telegram_user)

    @close_connection
    def show_progress(self, bot, chat_id, telegram_user):
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.mongo_client.find_one({'Order': progress.current_step_order})
        if progress.current_step_status == UserCourseProgress.STATUS_START:
            help_button = InlineKeyboardButton(text=bot_messages['help_now'],
                                               callback_data='ready')
            not_know_button = InlineKeyboardButton(text=bot_messages['not_know'],
                                                   callback_data='not_know')
            reply_markup = InlineKeyboardMarkup([[help_button], [not_know_button]])
            message = current_step['Problem']
        if progress.current_step_status == UserCourseProgress.STATUS_TEST:
            answers = [InlineKeyboardButton(text=each,
                                            callback_data='wrong') for each in current_step['Wrong_answers']] +\
                      [InlineKeyboardButton(text=current_step['Right_answer'],
                                            callback_data='right')]
            random.shuffle(answers)
            message = current_step['Problem']
            reply_markup = InlineKeyboardMarkup([[each] for each in answers])
        if progress.current_step_status == UserCourseProgress.STATUS_INFO:
            now_i_can_button = InlineKeyboardButton(text=bot_messages['now_i_can'],
                                                    callback_data='ready')
            message = current_step['Theoretical_part']
            if 'Video_url' in current_step:
                bot.sendVideo(chat_id=chat_id, video=current_step['Video_url'].encode('utf-8', 'strict'))
            elif 'Image_url' in current_step:
                bot.sendPhoto(chat_id=chat_id, photo=current_step['Image_url'].encode('utf-8', 'strict'))
            reply_markup = InlineKeyboardMarkup([[now_i_can_button]])
        bot.sendMessage(chat_id=chat_id,
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode=telegram.ParseMode.MARKDOWN)

    def hi(self, bot, update):
        print update
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text=bot_messages['hi'])
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')

    @close_connection
    def echo(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        if progress.current_step_status == UserCourseProgress.STATUS_END:
            bot.sendMessage(chat_id=chat_id,
                            text=bot_messages['finish'])
            return
        self.unknown(bot, update)

    def unknown(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        bot.sendMessage(chat_id=chat_id,
                        text=message)

    def die(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text='AAAAAAAA!!!! You kill me, motherfucker')
        bot.sendMessage(chat_id=chat_id, text="But I'll be back!!!!")
        self.updater.stop()

    def error(self, bot, update, error):
        print 'Update %s caused error %s' % (update, error)

    def reminder(self, bot, update):
        print 'reminder'
        chat_id = update.message.chat_id

        def job(bot):
            bot.sendMessage(chat_id=chat_id, text='30 seconds passed and I want to'
                                                  ' remind you that you are fucking idiot')

        self.j.put(job, 30, repeat=False)


print "start course bot"
