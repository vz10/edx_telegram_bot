# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from edx_telegram_bot.edx_telegram_bot import RaccoonBot


class Command(NoArgsCommand):
    def handle(self, **options):
        RaccoonBot()
