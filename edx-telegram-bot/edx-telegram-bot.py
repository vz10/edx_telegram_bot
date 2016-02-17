# -*- coding: utf-8 -*-

from telegram import Updater, ReplyKeyboardMarkup, Emoji, ChatAction
import telegram
from config import *
import re
import json
import requests
import time
import urllib

updater = Updater(token=token, workers=10)

dispatcher = updater.dispatcher

commands = {
    '/hi': 'Try it if you want to say hi to the Bot',
    '/courses': 'You can choose what kind of courses you are interesting in',
    '/all_courses': "You can see all available courses",
    '/my_courses': "You can see only your courses",
}

j = updater.job_queue


def hi(bot, update):
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


def get_course_description(bot, course_name, chat_id):
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


def echo(bot, update):
    chat_id = update.message.chat_id
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
    message = update.message.text
    print update
    if message.find(Emoji.THUMBS_UP_SIGN.decode('utf-8')) == 0:
        course_name = message[2:]
        get_course_description(bot, course_name, chat_id)
        return
    if message.find(Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8')) == 0:
        my_courses(bot, update)
        return
    if message.find(Emoji.ORANGE_BOOK.decode('utf-8')) == 0:
        courses(bot, update)
        return
    if message.find('hash::') == 0:
        sendHash(bot, update)
        return

    bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
    message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
    bot.sendMessage(chat_id=chat_id, text=message)


def unknown(bot, update):
    chat_id = update.message.chat_id
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
    message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
    bot.sendMessage(chat_id=chat_id,
                    text=message)


def die(bot, update):
    updater.stop()


def error(bot, update, error):
    print 'Update %s caused error %s' % (update, error)


def courses(bot, update):
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


def my_courses(bot, update):
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


def courses_menu(bot, update):
    chat_id = update.message.chat_id
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    bot.sendSticker(chat_id=chat_id, sticker='BQADBAADowMAAmONagABt5jVJ_gj0CEC')
    msg = "What kind of courses do you want me to find?"
    keyboard = [[Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8') + 'My courses'],
                [Emoji.ORANGE_BOOK.decode('utf-8') + 'All courses']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)


def help(bot, update):
    chat_id = update.message.chat_id
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
    time.sleep(1)
    bot.sendPhoto(chat_id=update.message.chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
    bot.sendMessage(chat_id=chat_id,
                    text="I have a lot of raccoon-workers, all of them want to help you, but they not very smart so they can understand only such commands:")

    for (command, description) in commands.items():
        bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)


def sendHash(bot, update):
    print 'sdfsdf'
    print update
    chat_id = update.message.chat_id
    user_hash = update.message.text
    response = requests.get(auth_api + '?token=' + str(user_hash) + '&tel_name=' + str(chat_id))
    if response.status_code == 200:
        bot.sendMessage(chat_id=chat_id, text="Registration OK")
    else:
        bot.sendMessage(chat_id=chat_id, text="Registration not OK")


def reminder(bot, update):
    print 'reminder'
    chat_id = update.message.chat_id

    def job(bot):
        bot.sendMessage(chat_id=chat_id, text='A single message with 30s delay')

    j.put(job, 30, repeat=False)


dispatcher.addTelegramCommandHandler('hi', hi)
dispatcher.addTelegramCommandHandler('die', die)
dispatcher.addTelegramCommandHandler('help', help)
dispatcher.addTelegramCommandHandler('reminder', reminder)
dispatcher.addTelegramCommandHandler('courses', courses_menu)
dispatcher.addTelegramCommandHandler('all_courses', courses)
dispatcher.addTelegramCommandHandler('my_courses', my_courses)

dispatcher.addTelegramMessageHandler(echo)
dispatcher.addTelegramRegexHandler(r"what.*course", courses)

dispatcher.addUnknownTelegramCommandHandler(unknown)
dispatcher.addErrorHandler(error)

updater.start_polling()
