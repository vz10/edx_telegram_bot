# -*- coding: utf-8 -*-

from telegram import Updater, ReplyKeyboardMarkup, Emoji
from config import *
import re
import json
import requests

updater = Updater(token=token)

dispatcher = updater.dispatcher

commands = {
    '/hi':'Try it if you want to say hi to the Bot',
    '/courses': 'Try it if you want to see all available courses'
}


j = updater.job_queue


def start(bot, update):
    print bot
    print '*'*50
    print update
    print '='*50
    bot.sendMessage(chat_id=update.message.chat_id, text="Fuck you, ugly motherfucker")

def echo(bot, update):
    message = "What do you mean with your fucking '"+update.message.text+"'?"
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=message)

def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=u"Ублюдок, мать твою, а ну иди сюда, говно собачье, решил ко мне лезть засранец вонючий, мать твою?! А, ну иди сюда, попробуй меня трахнуть, я тебя сам трахну ублюдок, анонист чертов, будь ты проклят, иди идиот, трахать тебя за свою семью, говно собачье, дерьмо, сука, падла, ну иди сюда мерзавец, негодяй, гад, иди сюда говно, жопа!")

def die(bot, update):
    updater.stoop()

def error(bot, update, error):
    print 'Update %s caused error %s' % (update, error)

def courses(bot, update):
    result = requests.get(courses_api).text
    result = json.loads(result)
    courses_lst = result.get('results')
    if not courses_lst:
        msg = 'Ублюдок, мать твою...'
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    else:
        msg = 'А вот и курсы, ублюдок, мать твою!'
        keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') + course['name']] for course in courses_lst]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)

def help(bot, update):
    chat_id=update.message.chat_id
    for (command, description) in commands.items(): 
        bot.sendMessage(chat_id=chat_id, text=command+' - '+description)

    bot.sendPhoto(chat_id=update.message.chat_id, photo='http://risovach.ru/upload/2014/08/mem/spanch-bob_58260721_orig_.jpg')

def keyboard(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='keyboard')
    print 'keyboard'
    custom_keyboard =  [[ "Fuck", "Fuck" ], [ "Fuck", "Fuck" ]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(chat_id=update.message.chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

def sendHash(bot, update):
    chat_id=update.message.chat_id
    user_hash = update.message.text
    response = requests.post("http://bugs.python.org", data={'hash': user_hash, 'telegram_id': chat_id})
    print response.status_code

def reminder(bot, update):
    print 'reminder'
    chat_id=update.message.chat_id
    def job(bot):
        bot.sendMessage(chat_id=chat_id, text='A single message with 30s delay')
    j.put(job, 30, repeat=False)


dispatcher.addTelegramCommandHandler('hi', start)
dispatcher.addTelegramCommandHandler('die', die)
dispatcher.addTelegramCommandHandler('help', help)
dispatcher.addTelegramCommandHandler('key', keyboard)
dispatcher.addTelegramCommandHandler('reminder', reminder)
dispatcher.addTelegramCommandHandler('courses', courses)

dispatcher.addTelegramMessageHandler(echo)
dispatcher.addTelegramRegexHandler(r"what.*course", courses)
dispatcher.addTelegramRegexHandler(r"hash*", sendHash)

dispatcher.addUnknownTelegramCommandHandler(unknown)
dispatcher.addErrorHandler(error)

updater.start_polling()
