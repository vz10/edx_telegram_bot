# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from edx_telegram_bot.edx_telegram_bot import RaccoonBot
from edx_telegram_bot.edx_course_bot import CourseBot


class Command(NoArgsCommand):
    def handle(self, **options):
        # RaccoonBot()
        CourseBot()
