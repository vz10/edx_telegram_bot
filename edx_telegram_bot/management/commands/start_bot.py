# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.conf import settings

from ...edx_telegram_bot import RaccoonBot
from ...edx_course_bot import CourseBot
from ...edx_course_xblock_bot import CourseBot as XblockCourseBot

from ...models import TelegramBot


class Command(NoArgsCommand):
    def handle(self, **options):
        RaccoonBot()
        CourseBot(token='187925341:AAFTaWDWkTDjFPOJLlA1ArRiK-Sviypx8QM', collection='111/111/111')
        map(lambda each: XblockCourseBot(token=each.token), TelegramBot.objects.all())
