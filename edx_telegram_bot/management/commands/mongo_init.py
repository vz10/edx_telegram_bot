# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ...bot_mongo import BotMongo

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('course_name', nargs='+', type=str)

    def handle(self, *args, **options):
        self.course_key = options['course_name'][0]
        self.mongo_client = BotMongo(database='bot', collection=self.course_key)
            #  Initial fixtures for mongo collection
        self.mongo_client.send({'Problem': 'I have a problem, do you know how to solve it',
                               'Right_answer': "Let's go",
                               'Wrong_answers': [],
                               'Positive_answer': "You are great, thanks",
                               'Order': 0,
                               'Next_step_order': 1})
        self.mongo_client.send({'Problem': 'I have a problem, do you know how to solve it',
                                    'Wrong_answers': ['First wrong answer', 'Second wrong answer', 'Third wrong answer'],
                                    'Right_answer': 'Right answer',
                                    'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
                                    'Negative_answer': "I can't belive that you are such an idiot",
                                    'Positive_answer': "You are great, thanks",
                                    'Order': 1,
                                    'Next_step_order': 2})
        self.mongo_client.send({'Problem': 'I have another problem, do you know how to solve it',
                                    'Wrong_answers': ['another First wrong answer', 'another Second wrong answer', 'another Third wrong answer'],
                                    'Right_answer': 'another Right answer',
                                    'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
                                    'Negative_answer': "I can't belive that you are such an idiot",
                                    'Positive_answer': "You are great, thanks",
                                    'Order': 2,
                                    'Next_step_order': 3})
