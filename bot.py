# -*- coding: utf-8 -*-

from telegram import Updater
from config import token
import re

updater = Updater(token=token)

dispatcher = updater.dispatcher

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
	message = 'What fucking course are you talking about'
	bot.sendMessage(chat_id=update.message.chat_id,
					text=message)

def help(bot, update):
	bot.sendPhoto(chat_id=update.message.chat_id, photo='http://risovach.ru/upload/2014/08/mem/spanch-bob_58260721_orig_.jpg')
	
def keyboard(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id,
					text='keyboard')
	print 'keyboard'
	custom_keyboard =  [[ "Fuck", "Fuck" ], [ "Fuck", "Fuck" ]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.sendMessage(chat_id=update.message.chat_id, text="Stay here, I'll be back.", reply_markup=reply_markup)

dispatcher.addTelegramCommandHandler('hi', start)
dispatcher.addTelegramCommandHandler('die', die)
dispatcher.addTelegramCommandHandler('help', help)
dispatcher.addTelegramCommandHandler('key', keyboard)

dispatcher.addTelegramMessageHandler(echo)
dispatcher.addTelegramRegexHandler(r"what.*course", courses)
dispatcher.addUnknownTelegramCommandHandler(unknown)
dispatcher.addErrorHandler(error)

updater.start_polling()
