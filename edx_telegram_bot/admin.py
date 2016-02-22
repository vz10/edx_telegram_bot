'''
django admin pages for edx-telegram bot model
'''

from models import EdxTelegramUser
from ratelimitbackend import admin

admin.site.register(EdxTelegramUser)

