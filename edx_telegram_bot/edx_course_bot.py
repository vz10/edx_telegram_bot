# -*- coding: utf-8 -*-

import time
from telegram import Updater, ReplyKeyboardMarkup, Emoji, ChatAction

from bot_mongo import BotMongo

from django.conf import settings
from models import (EdxTelegramUser, UserCourseProgress)
from edx_telegram_bot import is_telegram_user


class CourseBot(object):
    def __init__(self, **kwargs):
        """
        add commands and start bot
        :return:
        """

        self.commands = {
            '/hi': 'Try it if you want to say hi to the Bot',
            '/courses': 'You can choose what kind of courses you are interesting in',
            '/all_courses': "You can see all available courses",
            '/my_courses': "You can see only your courses",
            '/recommendations': "You can ask bot to recommend you some courses which will be interesting for you",
            # '/reminder': "In 30 seconds bot will remind you that you are idiot",
            # '/die': "Don't even think about it, motherfucker"
        }


        self.updater = Updater(token=settings.TELEGRAM_BOT.get('course_bot_token'), workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addTelegramCommandHandler('hi', self.hi)
        # self.dispatcher.addTelegramCommandHandler('die', self.die)
        self.dispatcher.addTelegramCommandHandler('help', self.help)
        # self.dispatcher.addTelegramCommandHandler('reminder', self.reminder)
        self.dispatcher.addTelegramCommandHandler('start', self.start)

        self.dispatcher.addTelegramMessageHandler(self.echo)

        self.dispatcher.addUnknownTelegramCommandHandler(self.unknown)
        self.dispatcher.addErrorHandler(self.error)

        self.queue = self.updater.start_polling()

        self.course_key = kwargs.get('collection', 'course_name')
        self.mongo_client = BotMongo(database='bot', collection=self.course_key)


        #Initial fixtures for mongo collection
        # self.mongo_client.send({'Problem': 'I have a problem, do you know how to solve it',
        #                         'Wrong_answers': ['First wrong answer', 'Second wrong answer', 'Third wrong answer'],
        #                         'Right_answer': 'Right answer',
        #                         'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
        #                         'Negative_answer': "I can't belive that you are such an idiot",
        #                         'Positive_answer': "You are great, thanks",
        #                         'Order': 0,
        #                         'Next_step_order':1})
        #
        # self.mongo_client.send({'Problem': 'I have another problem, do you know how to solve it',
        #                         'Wrong_answers': ['another First wrong answer', 'another Second wrong answer', 'another Third wrong answer'],
        #                         'Right_answer': 'another Right answer',
        #                         'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
        #                         'Negative_answer': "I can't belive that you are such an idiot",
        #                         'Positive_answer': "You are great, thanks",
        #                         'Order': 1,
        #                         'Next_step_order':2})
        # a = self.mongo_client.find_one({'field':'Content of that field'})

    @is_telegram_user
    def start(self, bot, update):
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress, cr = UserCourseProgress.objects.get_or_create(telegram_user=telegram_user, course_key=self.course_key)
        self.show_progress(bot, update)

    def show_progress(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.mongo_client.find_one({'Order': progress.current_step_order})
        if progress.current_step_status == UserCourseProgress.STATUS_START:
            keyboard = [[Emoji.FLEXED_BICEPS.decode('utf-8') + 'I can help you right now'],
                        [Emoji.ORANGE_BOOK.decode('utf-8') + 'I need to read something about it first']]
            message = current_step['Problem']
        if progress.current_step_status == UserCourseProgress.STATUS_TEST:
            answers = current_step['Wrong_answers'] + [current_step['Right_answer']]
            keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') + answer] for answer in answers]
            message = current_step['Problem']
        if progress.current_step_status == UserCourseProgress.STATUS_INFO:
            keyboard = [[Emoji.FLEXED_BICEPS.decode('utf-8') + 'Now I can help you']]
            message = current_step['Theoretical_part']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                        text=message,
                        reply_markup=reply_markup)

    def check_test(self, bot, update, answer):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        current_step = self.mongo_client.find_one({'Order': progress.current_step_order})
        if answer == current_step['Right_answer']:
            bot.sendMessage(chat_id=chat_id,
                            text=current_step['Positive_answer'])
            progress.current_step_status = UserCourseProgress.STATUS_START
            progress.current_step_order = current_step['Next_step_order']
            progress.save()
        else:
            bot.sendMessage(chat_id=chat_id,
                            text=current_step['Negative_answer'])
            progress.current_step_status = UserCourseProgress.STATUS_INFO
            progress.save()
        self.show_progress(bot, update)

    def hi(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text="Hello, human, I'm glad to see you")
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')

    def echo(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        progress = UserCourseProgress.objects.get(telegram_user=telegram_user, course_key=self.course_key)
        message = update.message.text
        if message.find(Emoji.THUMBS_UP_SIGN.decode('utf-8')) == 0:
            answer = message[1:]
            self.check_test(bot, update, answer)
            return
        if message.find(Emoji.ORANGE_BOOK.decode('utf-8')) == 0:
            progress.current_step_status = UserCourseProgress.STATUS_INFO
            progress.save()
            self.show_progress(bot, update)
            return
        if message.find(Emoji.FLEXED_BICEPS.decode('utf-8')) == 0:
            progress.current_step_status = UserCourseProgress.STATUS_TEST
            progress.save()
            self.show_progress(bot, update)
            return

        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        bot.sendMessage(chat_id=chat_id, text=message)

    def unknown(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
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

    def help(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=update.message.chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        bot.sendMessage(chat_id=chat_id,
                        text="I have a lot of raccoon-workers, all of them want to help you, but they not"\
                             " very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)

    def reminder(self, bot, update):
        print 'reminder'
        chat_id = update.message.chat_id

        def job(bot):
            bot.sendMessage(chat_id=chat_id, text='30 seconds passed and I want to'
                                                  ' remind you that you are fucking idiot')

        self.j.put(job, 30, repeat=False)


print "start course bot"

