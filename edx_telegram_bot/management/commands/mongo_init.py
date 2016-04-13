# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from bot_mongo import BotMongo



class Command(NoArgsCommand):
    def handle(self, **options):
           self.course_key = options.get('collection', 'course_name')
           self.mongo_client = BotMongo(database='bot', collection=self.course_key)
            #  Initial fixtures for mongo collection
           self.mongo_client.send({'Problem': 'I have a problem, do you know how to solve it',
                                    'Wrong_answers': ['First wrong answer', 'Second wrong answer', 'Third wrong answer'],
                                    'Right_answer': 'Right answer',
                                    'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
                                    'Negative_answer': "I can't belive that you are such an idiot",
                                    'Positive_answer': "You are great, thanks",
                                    'Order': 0,
                                    'Next_step_order':1})

            self.mongo_client.send({'Problem': 'I have another problem, do you know how to solve it',
                                    'Wrong_answers': ['another First wrong answer', 'another Second wrong answer', 'another Third wrong answer'],
                                    'Right_answer': 'another Right answer',
                                    'Theoretical_part': "Oh fucking idiot, you can not event distinguish wrong answer from right",
                                    'Negative_answer': "I can't belive that you are such an idiot",
                                    'Positive_answer': "You are great, thanks",
                                    'Order': 1,
                                    'Next_step_order':2})
