# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.conf import settings

from ...edx_telegram_bot import RaccoonBot
from ...edx_course_bot import CourseBot
from ...edx_course_xblock_bot import CourseBot

from ...models import TelegramBot


class Command(NoArgsCommand):
    def handle(self, **options):
        # RaccoonBot()
        # map(lambda each: CourseBot(token=each.bot.token,
        #                            collection=each.course_key),
        #     BotFriendlyCourses.objects.all())
        map(lambda each: CourseBot(token=each.token), TelegramBot.objects.all())

