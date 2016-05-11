# -*- coding: utf-8 -*-
from django.db import connection

from models import EdxTelegramUser

def is_telegram_user(f):
    def wrapper(*args, **kw):
        bot = args[1]
        update = args[2]
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        if not EdxTelegramUser.objects.filter(telegram_id=telegram_id):
            current_site = Site.objects.get_current()
            bot.sendMessage(chat_id=chat_id,
                            text="I don't know you, bro. You'd better go and register you telegram in edX first. On %s" % current_site)
            return
        return f(*args, **kw)
    return wrapper


def close_connection(f):
    def wrapper(*args, **kwargs):
        retval = f(*args, **kwargs)
        connection.close()
        return retval
    return wrapper