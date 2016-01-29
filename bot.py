# -*- coding: utf-8 -*-

from telegram import Updater

updater = Updater(token='')

dispatcher = updater.dispatcher

def start(bot, update):
   print bot
   print '*'*50
   print update
   print '='*50
   bot.sendMessage(chat_id=update.message.chat_id, text="Fuck you, ugly motherfucker")

def echo(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id,
					text="What do you mean with your fucking '"+update.message.text+"'?" )

def unknown(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id,
					text=u"Ублюдок, мать твою, а ну иди сюда, говно собачье, решил ко мне лезть засранец вонючий, мать твою?! А, ну иди сюда, попробуй меня трахнуть, я тебя сам трахну ублюдок, анонист чертов, будь ты проклят, иди идиот, трахать тебя за свою семью, говно собачье, дерьмо, сука, падла, ну иди сюда мерзавец, негодяй, гад, иди сюда говно, жопа!")

def die(bot, update):
	updater.stoop()

dispatcher.addTelegramCommandHandler('hi', start)
dispatcher.addTelegramCommandHandler('die', die)
dispatcher.addUnknownTelegramCommandHandler(unknown)
dispatcher.addTelegramMessageHandler(echo)

updater.start_polling()
