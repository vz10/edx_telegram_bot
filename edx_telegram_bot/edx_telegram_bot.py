# -*- coding: utf-8 -*-
import re
import time
import json
import telegram
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton, ChatAction,
                      Emoji, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, CallbackQueryHandler

from django.contrib.sites.models import Site
from django.conf import settings

from openedx.core.djangoapps.models.course_details import CourseDetails
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.locator import CourseLocator
from course_modes.models import CourseMode
from student.models import CourseEnrollment, AlreadyEnrolledError, EnrollmentClosedError

import prediction
from models import (MatrixEdxCoursesId, TfidMatrixAllCourses, UserLocation,
                    EdxTelegramUser, TfidUserVector, LearningPredictionForUser,
                    PredictionForUser, BotFriendlyCourses)
from decorators import is_telegram_user, close_connection


def truncate_course_info(course_info):
    course_info = re.sub('<[^>]*>', '', course_info).split()
    if len(course_info) > 35:
        return ' '.join(course_info[:35]) + '...'
    else:
        return ' '.join(course_info)


class RaccoonBot(object):
    def __init__(self):
        """
        add commands and start bot
        :return:
        """

        self.commands = {
            '/hi': 'Try it if you want to say hi to the Bot',
            '/all_courses': "You can see all available courses",
            '/my_courses': "You can see only your courses",
            '/recommendations': "You can ask bot to recommend you some courses which will be interesting for you",
            # '/reminder': "In 30 seconds bot will remind you that you are idiot",
            # '/die': "Don't even think about it, motherfucker"
        }

        prediction.get_coursed_and_create_matrix()

        self.updater = Updater(token=settings.TELEGRAM_BOT.get('token'), workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addHandler(CommandHandler('hi', self.hi_command))
        # self.dispatcher.addHandler(CommandHandler('die', self.die))
        # self.dispatcher.addHandler(CommandHandler('reminder', self.reminder))
        self.dispatcher.addHandler(CommandHandler('help', self.help_command))
        self.dispatcher.addHandler(CommandHandler('all_courses', self.courses_command))
        self.dispatcher.addHandler(CommandHandler('my_courses', self.my_courses_command))
        self.dispatcher.addHandler(CommandHandler('start', self.send_hash_command))
        self.dispatcher.addHandler(CommandHandler('recommendations', self.recommend_command))
        self.dispatcher.addHandler(CommandHandler('location', self.location))

        self.dispatcher.addHandler(MessageHandler([Filters.text], self.echo))
        self.dispatcher.addHandler(MessageHandler([Filters.location], self.get_location))
        self.dispatcher.addHandler(CallbackQueryHandler(self.inline_keyboard))

        self.dispatcher.addErrorHandler(self.error)
        self.dispatcher.addHandler(RegexHandler(r'/.*', self.unknown))

        self.queue = self.updater.start_polling()

    def location(self, bot, update):
        chat_id = update.message.chat_id
        get_location = KeyboardButton(text='tell mew where you are',
                                      request_location=True)
        reply_markup = ReplyKeyboardMarkup(keyboard=[[get_location]], one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id,
                        text="Ok I'm waiting for your checkin",
                        reply_markup=reply_markup)

    @close_connection
    def enroll_user(self, bot, chat_id, telegram_user, course_id, show_description=True):
        user = telegram_user.student
        if isinstance(course_id, CourseLocator):
            course_key = course_id
        else:
            course_key = CourseKey.from_string(course_id)
        if CourseMode.can_auto_enroll(course_key):
            available_modes = CourseMode.modes_for_course_dict(course_key)
            try:
                enroll_mode = CourseMode.auto_enroll_mode(course_key, available_modes)
                if enroll_mode:
                    CourseEnrollment.enroll(user, course_key, check_access=True, mode=enroll_mode)
                if not BotFriendlyCourses.objects.filter(course_key=course_key).exists():
                    bot.sendMessage(chat_id=chat_id,
                                    text="You've been enrolled")
                    if show_description:
                        self.get_course_description(bot, chat_id, course_name=None, course_key=course_key)
            except AlreadyEnrolledError:
                bot.sendMessage(chat_id=chat_id,
                                text="It seems like you've been already enrolled to that course")
            except EnrollmentClosedError:
                bot.sendMessage(chat_id=chat_id,
                                text="I'm sorry but enrollment to that course has been closes")
            except Exception as e:
                print e
                bot.sendMessage(chat_id=chat_id,
                                text="Something goes wrong")

    @is_telegram_user
    def get_location(self, bot, update):
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        UserLocation.objects.create(telegram_user=telegram_user,
                                    longitude=longitude,
                                    latitude=latitude)
        bot.sendMessage(chat_id=chat_id,
                        text='Thank you, bro',
                        reply_markup=ReplyKeyboardHide())

    @is_telegram_user
    def recommend_command(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        self.recommend(bot, chat_id, telegram_user)

    @close_connection
    @is_telegram_user
    def my_courses_command(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.filter(telegram_id=telegram_id).first()
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        results = CourseEnrollment.enrollments_for_user(telegram_user.student)
        if not results:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADMwIAAmONagABu635srr8N-0C')
            msg = "I can't find any courses for you. Sorry"
            bot.sendMessage(chat_id=chat_id, text=msg)
        else:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADCwIAAmONagABF1QQKl9NWncC')
            msg = "Just have a look what I've found for you"
            keyboard = [InlineKeyboardButton(text=modulestore().get_course(course.course_id).display_name_with_default,
                                             callback_data=json.dumps({'method': 'get_course_description',
                                                                       'kwargs': {'enroll': course.id}}))
                        for course in results]

            reply_markup = InlineKeyboardMarkup([[each] for each in keyboard])
            bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def help_command(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=update.message.chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        bot.sendMessage(chat_id=chat_id,
                        text="I have a lot of raccoon-workers, all of them want to help you, but they not very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)

    def send_hash_command(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        user_hash = update.message.text[7:]
        try:
            edx_telegram_user = EdxTelegramUser.objects.get(hash=user_hash)
            edx_telegram_user.telegram_id = telegram_id
            edx_telegram_user.status = EdxTelegramUser.STATUS_ACTIVE
            edx_telegram_user.save()
            bot.sendMessage(chat_id=chat_id, text="Registration successful")
        except EdxTelegramUser.DoesNotExist:
            if EdxTelegramUser.objects.filter(telegram_id=telegram_id).exists():
                bot.sendMessage(chat_id=chat_id, text="Nice to see you again")
            else:
                bot.sendMessage(chat_id=chat_id, text="Auth token doesn't correct")

    @close_connection
    def recommend(self, bot, chat_id, telegram_user):
        telegram_id = telegram_user.telegram_id
        if not LearningPredictionForUser.objects.filter(telegram_user=telegram_user):
            bot.sendMessage(chat_id=chat_id,
                            text="It seems like I see you for the first time,"\
                                    " please answer a few questions, so I'll be know more about you")
            prediction.get_test_courses(telegram_id)
        test_courses = LearningPredictionForUser.objects.get(telegram_user=telegram_user).get_list()
        if len(test_courses) > 0:
            course_id = MatrixEdxCoursesId.objects.filter(course_index=test_courses[0]).first().course_key
            course_key = CourseKey.from_string(course_id)
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='I like it!',
                                       callback_data=json.dumps({'method': 'learning',
                                                                 'kwargs': {}}))],
                 [InlineKeyboardButton(text="Hmmm. I don't like at all!",
                                       callback_data=json.dumps({'method': 'learning',
                                                                 'kwargs': {'is_positive': False}}))]])
        else:
            predicted_course_id = prediction.prediction(telegram_id)

            if predicted_course_id == -1:
                bot.sendMessage(chat_id=chat_id,
                                text="It seems like you have enrolled to all courses we have for now")
                return

            predicted_course_key = MatrixEdxCoursesId.objects.filter(course_index=predicted_course_id)\
                                                             .first().course_key
            bot.sendMessage(chat_id=chat_id,
                            text="Now I'm going to recommend you some great courses")
            course_key = CourseKey.from_string(predicted_course_key)

            course_for_user = PredictionForUser.objects.get_or_create(telegram_user=telegram_user)[0]
            course_for_user.prediction_course = predicted_course_key
            course_for_user.save()
            reply_markup = InlineKeyboardMarkup(
                       [[InlineKeyboardButton(text='I like it and I want to enroll',
                                              callback_data=json.dumps({'method': 'enroll',
                                                                        'kwargs': {}}))],
                        [InlineKeyboardButton(text='I like it but will eroll another time',
                                              callback_data=json.dumps({'method': 'not_enroll',
                                                                        'kwargs': {}}))],
                        [InlineKeyboardButton(text="What the shit is this (I don't like it)",
                                              callback_data=json.dumps({'method': 'wrong_predict',
                                                                        'kwargs': {}}))]])

        course_description = CourseDetails.fetch_about_attribute(course_key, 'overview')
        course_title = modulestore().get_course(course_key).display_name_with_default
        bot.sendMessage(chat_id=chat_id,
                        text='*%s*' % course_title,
                        parse_mode=telegram.ParseMode.MARKDOWN)
        bot.sendMessage(chat_id=chat_id,
                        text=truncate_course_info(course_description),
                        reply_markup=reply_markup)

    def courses_command(self, bot, update):
        """
        Get list of all available courses in edX database
        """
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        results = modulestore().get_courses()
        results = [course for course in results if
                   course.scope_ids.block_type == 'course']

        if not results:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADMwIAAmONagABu635srr8N-0C')
            msg = "I can't find any courses for you. Sorry"
            bot.sendMessage(chat_id=chat_id, text=msg)
        else:
            bot.sendSticker(chat_id=chat_id, sticker='BQADBAADCwIAAmONagABF1QQKl9NWncC')
            msg = "Just have a look what I've found for you"
            keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') +
                         modulestore().get_course(course.id).display_name_with_default] for course in results]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def hi_command(self, bot, update):
        """
        Answer on hi command of user
        """
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text="Hello, human, I'm glad to see you")
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')

    def learning(self, bot, chat_id, telegram_user, is_positive=True):
        """
        Update user TfIdf vector depending on user reaction for recommendations
        """
        learning_lessons = LearningPredictionForUser.objects.get(telegram_user=telegram_user)
        if is_positive:
            user_vector, cr = TfidUserVector.objects.get_or_create(telegram_user=telegram_user)
            matrix = TfidMatrixAllCourses.objects.all().first().matrix
            if cr:
                user_vector.vector = matrix[learning_lessons.get_list()[0]]
            else:
                user_vector.vector = user_vector.vector+matrix[learning_lessons.get_list()[0]]
            user_vector.save()
        learning_lessons.save_list(learning_lessons.get_list()[1:])
        bot.sendMessage(chat_id=chat_id, text="Ok, let's go on")
        self.recommend(bot, chat_id, telegram_user)

    def predict_answer(self, bot, chat_id, telegram_user, enroll=False, yes=False):
        predicted_course_id = PredictionForUser.objects.get(telegram_user=telegram_user).prediction_course
        answer_id = MatrixEdxCoursesId.objects.filter(course_key=predicted_course_id).first().course_index
        prediction.i_am_going_to_teach_you(telegram_user, answer_id, is_right=yes)
        if enroll:
            self.enroll_user(bot, chat_id, telegram_user, predicted_course_id, show_description=False)
        PredictionForUser.objects.get(telegram_user=telegram_user).delete()

    def enroll(self, bot, chat_id, telegram_user, **kwargs):
        self.predict_answer(bot, chat_id, telegram_user, enroll=True, yes=True)

    def not_enroll(self, bot, chat_id, telegram_user, **kwargs):
        self.predict_answer(bot, chat_id, telegram_user, yes=True)
        text = "Thank you for your answer, it will help me to improve my recommendations in future"
        sticker = 'BQADBAAD-QEAAmONagABI1o6OFspgIIC'
        bot.sendSticker(chat_id=chat_id, sticker=sticker)
        bot.sendMessage(chat_id=chat_id, text=text)

    def wrong_predict(self, bot, chat_id, telegram_user, **kwargs):
        self.predict_answer(bot, chat_id, telegram_user)
        text = "Sorry for that bad recommendation, I'll try to give better advices in future. "
        sticker = 'BQADBAADAwIAAmONagABc-jLpvC0yP8C'
        bot.sendSticker(chat_id=chat_id, sticker=sticker)
        bot.sendMessage(chat_id=chat_id, text=text)

    def inline_keyboard(self, bot, update):
        print update
        answer = json.loads(update.callback_query.data)
        telegram_id = update.callback_query.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        text = update.callback_query.message.text
        bot.editMessageText(chat_id=chat_id, message_id=message_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
        if 'key' in answer:
            self.enroll_user(bot, chat_id, telegram_user, answer['key'], show_description=False)
        else:
            getattr(self, answer['method'])(bot, chat_id, telegram_user, **answer['kwargs'])

    def get_course_description(self, bot, chat_id, course_name=None, course_key=None,
                               enroll=None, enroll_keyboard=False):
        """
        Get description of particular courses by Title or by course_id
        """
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        if enroll:
            result = CourseEnrollment.objects.get(id=enroll)
            results = [modulestore().get_course(result.course_id)]
            course_name = results[0].display_name_with_default
        elif course_key:
            results = [modulestore().get_course(course_key)]
            course_name = modulestore().get_course(course_key).display_name_with_default
        else:
            results = modulestore().get_courses()
            results = [course for course in results if
                       course.scope_ids.block_type == 'course']
        for each in results:
            if each.display_name_with_default == course_name:
                message = truncate_course_info(CourseDetails.fetch_about_attribute(each.id, 'overview'))
                if message == 'null':
                    bot.sendMessage(chat_id=chat_id, text="I'm sorry, but this course has no description")
                else:
                    bot.sendMessage(chat_id=chat_id, text="*Short course description*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    course_key = each.id
                    current_site = Site.objects.get_current()
                    course_title = modulestore().get_course(course_key).display_name_with_default
                    course_url = '[%s](%scourses/%s/)' % (course_title, current_site, each.id)
                    bot.sendMessage(chat_id=chat_id,
                                    text=course_url,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    if enroll_keyboard:
                        reply_markup = InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text='I like it and I want to enroll',
                                                   callback_data=json.dumps({'key': str(course_key)}))]])
                        bot.sendMessage(chat_id=chat_id, text=message, reply_markup=reply_markup)
                    else:
                        bot.sendMessage(chat_id=chat_id, text=message)
                break
        bot.sendMessage(chat_id=chat_id, reply_markup=ReplyKeyboardHide())

    def echo(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        message = update.message.text
        text = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        sticker = 'BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg'
        reply_markup = telegram.ReplyKeyboardMarkup([[]])
        if message[0] == Emoji.THUMBS_UP_SIGN.decode('utf-8'):
            course_name = message[1:]
            self.get_course_description(bot, chat_id, course_name, enroll_keyboard=True)
            return
        bot.sendSticker(chat_id=chat_id, sticker=sticker)
        bot.sendMessage(chat_id=chat_id, text=text)
        bot.sendMessage(chat_id=chat_id, reply_markup=reply_markup)

    def unknown(self, bot, update):
        """
        Handle non dispathed Telegram commands
        """
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        bot.sendMessage(chat_id=chat_id,
                        text=message)

    def die(self, bot, update):
        """
        Dev method to kill bot
        """
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text='AAAAAAAA!!!! You kill me, motherfucker')
        bot.sendMessage(chat_id=chat_id, text="But I'll be back!!!!")
        self.updater.stop()

    def error(self, bot, update, error):
        print 'Update %s caused error %s' % (update, error)

    def reminder(self, bot, update):
        chat_id = update.message.chat_id

        def job(bot):
            bot.sendMessage(chat_id=chat_id, text='30 seconds passed and I want to remind'
                                                  ' you that you are fucking idiot')

        self.j.put(job, 30, repeat=False)
