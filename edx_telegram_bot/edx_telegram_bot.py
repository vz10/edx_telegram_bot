# -*- coding: utf-8 -*-


from telegram import Updater, ReplyKeyboardMarkup, Emoji, ChatAction
import telegram
from decorators import singleton
from config import *
import json
import requests
import time
import urllib

import prediction

class RaccoonBot(object):
    def __init__(self):
        """
        add commands and start bot
        :return:
        """

        self.commands = {
            '/hi': 'Try it if you want to say hi to the Bot',
            '/courses': 'You can choose what kind of courses you are interesting in',
            '/all_courses': "You can see all available courses",
            '/my_courses': "You can see only your courses",
        }

        prediction.get_coursed_and_create_matrix()

        print "*" * 88
        print "run bot"
        self.updater = Updater(token=token, workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addTelegramCommandHandler('hi', self.hi)
        self.dispatcher.addTelegramCommandHandler('die', self.die)
        self.dispatcher.addTelegramCommandHandler('help', self.help)
        self.dispatcher.addTelegramCommandHandler('reminder', self.reminder)
        self.dispatcher.addTelegramCommandHandler('courses', self.courses_menu)
        self.dispatcher.addTelegramCommandHandler('all_courses', self.courses)
        self.dispatcher.addTelegramCommandHandler('my_courses', self.my_courses)

        self.dispatcher.addTelegramMessageHandler(self.echo)
        self.dispatcher.addTelegramRegexHandler(r"what.*course", self.courses)

        self.dispatcher.addUnknownTelegramCommandHandler(self.unknown)
        self.dispatcher.addErrorHandler(self.error)

        self.queue = self.updater.start_polling()

    def hi(self, bot, update):
        print bot
        print '*' * 50
        print update
        print '=' * 50
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendMessage(chat_id=chat_id, text="Hello, human, I'm glad to see you")
        try:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')
        except e:
            print e

    def get_course_description(self, bot, course_name, chat_id):
        result = requests.get(courses_api).text
        result = json.loads(result)
        courses_lst = result.get('results')
        for each in courses_lst:
            if each['name'] == course_name:
                course_id = urllib.pathname2url(each['id'])
                result = requests.get(description_api + course_id).text
                result = json.loads(result)
                message = result['short_description']
                if message == 'null':
                    bot.sendMessage(chat_id=chat_id, text="I'm sorry, but this course has no description")
                else:
                    bot.sendMessage(chat_id=chat_id, text="*Short course description*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.sendMessage(chat_id=chat_id, text=message)

    def echo(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        message = update.message.text
        print update
        if message.find(Emoji.THUMBS_UP_SIGN.decode('utf-8')) == 0:
            course_name = message[2:]
            self.get_course_description(bot, course_name, chat_id)
            return
        if message.find(Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8')) == 0:
            self.my_courses(bot, update)
            return
        if message.find(Emoji.ORANGE_BOOK.decode('utf-8')) == 0:
            self.courses(bot, update)
            return
        if message.find('hash::') == 0:
            self.send_hash(bot, update)
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
        self.updater.stop()

    def error(self, bot, update, error):
        print 'Update %s caused error %s' % (update, error)

    def courses(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        result = requests.get(courses_api).text
        result = json.loads(result)
        courses_lst = result.get('results')
        if not courses_lst:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADMwIAAmONagABu635srr8N-0C')
            msg = "I can't find any courses for you. Sorry"
            bot.sendMessage(chat_id=chat_id, text=msg)
        else:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADCwIAAmONagABF1QQKl9NWncC')
            msg = "Just have a look what I've found for you"
            keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') + course['name']] for course in courses_lst]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def my_courses(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)

        response = requests.get(enroll_api + '?tel_name=' + str(chat_id)).text

        result = json.loads(response)
        courses_lst = result.get('courses')
        if not courses_lst:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADMwIAAmONagABu635srr8N-0C')
            msg = "I can't find any courses for you. Sorry"
            bot.sendMessage(chat_id=chat_id, text=msg)
        else:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADCwIAAmONagABF1QQKl9NWncC')
            msg = "Just have a look what I've found for you"
            keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') + course['course_name']] for course in courses_lst]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def courses_menu(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAADowMAAmONagABt5jVJ_gj0CEC')
        msg = "What kind of courses do you want me to find?"
        keyboard = [[Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8') + 'My courses'],
                    [Emoji.ORANGE_BOOK.decode('utf-8') + 'All courses']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def help(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=update.message.chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        bot.sendMessage(chat_id=chat_id,
                        text="I have a lot of raccoon-workers, all of them want to help you, but they not very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)

    def send_hash(self, bot, update):
        print 'send hash'
        print update
        chat_id = update.message.chat_id
        user_hash = update.message.text
        response = requests.get(auth_api + '?token=' + str(user_hash) + '&tel_name=' + str(chat_id))
        if response.status_code == 200:
            bot.sendMessage(chat_id=chat_id, text="Registration OK")
        else:
            bot.sendMessage(chat_id=chat_id, text="Registration not OK")

    def reminder(self, bot, update):
        print 'reminder'
        chat_id = update.message.chat_id

        def job(bot):
            bot.sendMessage(chat_id=chat_id, text='A single message with 30s delay')

        self.j.put(job, 30, repeat=False)


print "start"

