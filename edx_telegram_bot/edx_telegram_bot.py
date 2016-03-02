# -*- coding: utf-8 -*-
import re
import time
import telegram
from telegram import Updater, ReplyKeyboardMarkup, Emoji, ChatAction

from django.contrib.sites.models import Site

from openedx.core.djangoapps.models.course_details import CourseDetails
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from course_modes.models import CourseMode
from student.models import CourseEnrollment, AlreadyEnrolledError

import prediction

from django.conf import settings
from models import (MatrixEdxCoursesId, TfidMatrixAllCourses,
                    EdxTelegramUser, TfidUserVector, LearningPredictionForUser,
                    PredictionForUser)


def truncate_course_info(course_info):
    course_info = re.sub('<[^>]*>', '', course_info).split()
    if len(course_info) > 35:
        return ' '.join(course_info[:35]) + '...'
    else:
        return ' '.join(course_info)


def is_telegram_user(f):
    def wrapper(*args, **kw):
        bot = args[1]
        update = args[2]
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        if not EdxTelegramUser.objects.filter(telegram_id=telegram_id):
            bot.sendMessage(chat_id=chat_id,
                            text="I don't know you, bro. You'd better go and register you telegram in edX first")
            return
        return f(*args, **kw)
    return wrapper


class RaccoonBot(object):
    def __init__(self):
        """
        add commands and start bot
        :return:
        """

        self.commands = {
            '/hi': 'Try it if you want to say hi to the Bot',
            '/courses': 'You can choose what kind of courses you are interesting in',
            '/all_courses': "You can see all available courses",
            '/my_courses': "You can see only your courses",
            '/recommendations': "You can ask bot to recommend you some courses which will be interesting for you",
            '/reminder': "In 30 seconds bot will remind you that you are idiot",
            '/die': "Don't even think about it, motherfucker"
        }

        prediction.get_coursed_and_create_matrix()

        print "*" * 88
        print "run bot"
        self.updater = Updater(token=settings.TELEGRAM_BOT.get('token'), workers=10)
        self.dispatcher = self.updater.dispatcher
        self.j = self.updater.job_queue

        self.dispatcher.addTelegramCommandHandler('hi', self.hi)
        self.dispatcher.addTelegramCommandHandler('die', self.die)
        self.dispatcher.addTelegramCommandHandler('help', self.help)
        self.dispatcher.addTelegramCommandHandler('reminder', self.reminder)
        self.dispatcher.addTelegramCommandHandler('courses', self.courses_menu)
        self.dispatcher.addTelegramCommandHandler('all_courses', self.courses)
        self.dispatcher.addTelegramCommandHandler('my_courses', self.my_courses)
        self.dispatcher.addTelegramCommandHandler('recommendations', self.recommend)

        self.dispatcher.addTelegramMessageHandler(self.echo)
        self.dispatcher.addTelegramRegexHandler(r"what.*course", self.courses)

        self.dispatcher.addUnknownTelegramCommandHandler(self.unknown)
        self.dispatcher.addErrorHandler(self.error)

        self.queue = self.updater.start_polling()

    def enroll_user(self, bot, update, course_id):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        user = telegram_user.student
        course_key = CourseKey.from_string(course_id)
        if CourseMode.can_auto_enroll(course_key):
            available_modes = CourseMode.modes_for_course_dict(course_key)
            try:
                enroll_mode = CourseMode.auto_enroll_mode(course_key, available_modes)
                if enroll_mode:
                    CourseEnrollment.enroll(user, course_key, check_access=True, mode=enroll_mode)
                bot.sendMessage(chat_id=chat_id,
                                text="You've been enrolled")
                course_title = modulestore().get_course(course_key).display_name_with_default
                self.get_course_description(bot, update, course_title)
            except AlreadyEnrolledError:
                bot.sendMessage(chat_id=chat_id,
                                text="It seems like you've been already enrolled, fucking idiot")
            except Exception:
                bot.sendMessage(chat_id=chat_id,
                                text="Something goes wrong")

    @is_telegram_user
    def recommend(self, bot, update):
        chat_id = update.message.chat_id
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        if not LearningPredictionForUser.objects.filter(telegram_user=telegram_user):
            bot.sendMessage(chat_id=chat_id,
                            text="It seems like I see you for the first time,"\
                                 " please answer a few questions, so I'll be know more about you")
            prediction.get_test_courses(telegram_id)
        test_courses = LearningPredictionForUser.objects.get(telegram_user=telegram_user).get_list()
        if len(test_courses) > 0:
            course_id = MatrixEdxCoursesId.objects.get(course_index=test_courses[0]).course_key
            course_key = CourseKey.from_string(course_id)
            keyboard = [[Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8') + 'I like it'],
                        [Emoji.ORANGE_BOOK.decode('utf-8') + 'What the shit is this']]
        else:
            predicted_course_id = prediction.prediction(telegram_id)

            if predicted_course_id == -1:
                bot.sendMessage(chat_id=chat_id,
                                text="It seems like you have enrolled to all courses we have for now")
                return

            predicted_course_key = MatrixEdxCoursesId.objects.get(course_index=predicted_course_id).course_key
            bot.sendMessage(chat_id=chat_id,
                            text="Now I'm going to recommend you some shitty courses")
            course_key = CourseKey.from_string(predicted_course_key)

            course_for_user = PredictionForUser.objects.get_or_create(telegram_user=telegram_user)[0]
            course_for_user.prediction_course = predicted_course_key
            course_for_user.save()

            keyboard = [[Emoji.FLEXED_BICEPS.decode('utf-8') + 'I like it and I want to enroll'],
                        [Emoji.YELLOW_HEART.decode('utf-8') + 'I like it but will eroll another time'],
                        [Emoji.PILE_OF_POO.decode('utf-8') + 'What the shit is this']]

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        course_description = CourseDetails.fetch_about_attribute(course_key, 'overview')
        course = modulestore().get_course(course_key)
        course_title = modulestore().get_course(course_key).display_name_with_default
        bot.sendMessage(chat_id=chat_id,
                        text='*%s*' % course_title,
                        parse_mode=telegram.ParseMode.MARKDOWN)
        bot.sendMessage(chat_id=chat_id,
                        text=truncate_course_info(course_description),
                        reply_markup=reply_markup)

    def learning(self, bot, update, is_positive=True):
        chat_id = update.message.chat_id
        telegram_id =  update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
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
        self.recommend(bot, update)

    def predict_answer(self, bot, update, enroll=False, yes=False):
        telegram_id = update.message.from_user.id
        telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
        predicted_course_id = PredictionForUser.objects.get(telegram_user=telegram_user).prediction_course
        answer_id = MatrixEdxCoursesId.objects.get(course_key=predicted_course_id).course_index
        prediction.i_am_going_to_teach_you(telegram_id, answer_id, is_right=yes)
        if enroll:
            self.enroll_user(bot, update, predicted_course_id)
        PredictionForUser.objects.get(telegram_user=telegram_user).delete()

    def hi(self, bot, update):
        print bot
        print '*' * 50
        print update.message.from_user.id
        print '=' * 50
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text="Hello, human, I'm glad to see you")
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD7wEAAmONagABIoEfTRQCUCQC')

    def get_course_description(self, bot, update, course_name):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
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
                    print each
                    course_key = each.id
                    current_site = Site.objects.get_current()
                    course_title = modulestore().get_course(course_key).display_name_with_default
                    course_url = '[%s](%scourses/%s/)' % (course_title, current_site, each.id)
                    bot.sendMessage(chat_id=chat_id,
                                    text=course_url,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    bot.sendMessage(chat_id=chat_id, text=message)

    def echo(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        message = update.message.text
        print update
        if message.find(Emoji.THUMBS_UP_SIGN.decode('utf-8')) == 0:
            course_name = message[1:]
            self.get_course_description(bot, update, course_name)
            return
        if message.find(Emoji.KISSING_FACE_WITH_CLOSED_EYES.decode('utf-8')) == 0:
            self.learning(bot, update)
            return
        if message.find(Emoji.ORANGE_BOOK.decode('utf-8')) == 0:
            self.learning(bot, update, is_positive=False)
            return
        if message.find(Emoji.FLEXED_BICEPS.decode('utf-8')) == 0:
            self.predict_answer(bot, update, enroll=True, yes=True)
            return
        if message.find(Emoji.YELLOW_HEART.decode('utf-8')) == 0:
            self.predict_answer(bot, update, yes=True)
            return
        if message.find(Emoji.PILE_OF_POO.decode('utf-8')) == 0:
            self.predict_answer(bot, update)
            return
        if message.find(Emoji.T_SHIRT.decode('utf-8')) == 0:
            self.my_courses(bot, update)
            return
        if message.find(Emoji.FATHER_CHRISTMAS.decode('utf-8')) == 0:
            self.courses(bot, update)
            return
        if message.find('hash::') == 0:
            self.send_hash(bot, update)
            return

        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        bot.sendMessage(chat_id=chat_id, text=message)

    def unknown(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAAD-wEAAmONagABdGfTKC1oAAGjAg')
        message = "Sorry, bro. I'm just a little raccoon and I don't know such words. Maybe you'll try /help page to improve our communication?"
        bot.sendMessage(chat_id=chat_id,
                        text=message)

    def die(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=chat_id, text='AAAAAAAA!!!! You kill me, motherfucker')
        bot.sendMessage(chat_id=chat_id, text="But I'll be back!!!!")
        self.updater.stop()

    def error(self, bot, update, error):
        print 'Update %s caused error %s' % (update, error)

    def courses(self, bot, update):
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

    @is_telegram_user
    def my_courses(self, bot, update):
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
            keyboard = [[Emoji.THUMBS_UP_SIGN.decode('utf-8') +
                         modulestore().get_course(course.course_id).display_name_with_default] for course in results]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def courses_menu(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendSticker(chat_id=chat_id, sticker='BQADBAADowMAAmONagABt5jVJ_gj0CEC')
        msg = "What kind of courses do you want me to find?"
        keyboard = [[Emoji.T_SHIRT.decode('utf-8') + 'My courses'],
                    [Emoji.FATHER_CHRISTMAS.decode('utf-8') + 'All courses']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=reply_markup)

    def help(self, bot, update):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendPhoto(chat_id=update.message.chat_id, photo='https://raccoongang.com/media/img/raccoons.jpg')
        bot.sendMessage(chat_id=chat_id,
                        text="I have a lot of raccoon-workers, all of them want to help you, but they not very smart so they can understand only such commands:")

        for (command, description) in self.commands.items():
            bot.sendMessage(chat_id=chat_id, text=command + ' - ' + description)

    def send_hash(self, bot, update):
        print 'send hash'
        print update
        chat_id = update.message.chat_id
        user_hash = update.message.text
        try:
            edx_telegram_user = EdxTelegramUser.objects.get(hash=user_hash)
            edx_telegram_user.telegram_id = chat_id
            edx_telegram_user.status = EdxTelegramUser.STATUS_ACTIVE
            edx_telegram_user.save()
            bot.sendMessage(chat_id=chat_id, text="Registration successful")
        except EdxTelegramUser.DoesNotExist:
            bot.sendMessage(chat_id=chat_id, text="Auth token doesn't correct")

    def reminder(self, bot, update):
        print 'reminder'
        chat_id = update.message.chat_id

        def job(bot):
            bot.sendMessage(chat_id=chat_id, text='30 seconds passed and I want to remind'
                                                  ' you that you are fucking idiot')

        self.j.put(job, 30, repeat=False)


print "start"
