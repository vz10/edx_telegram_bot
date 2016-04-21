import hashlib
import json

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from opaque_keys.edx.locator import CourseLocator
from xmodule.modulestore.django import modulestore
from django.db.models.signals import pre_save, post_save

from picklefield.fields import PickledObjectField
from django.conf import settings

from django.dispatch import receiver
from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

import telegram


# method for updating
@receiver(pre_save, sender=CourseEnrollment)
def someone_enrolls(sender, instance, **kwargs):
    bot = telegram.Bot(token=settings.TELEGRAM_BOT.get('token'))
    prev_enrollment = CourseEnrollment.objects.filter(user=instance.user, course_id=instance.course_id).exists()
    telegram_user = EdxTelegramUser.objects.filter(student=instance.user).first()
    if instance.is_active and not prev_enrollment and telegram_user:
        course_bot = BotFriendlyCourses.objects.filter(course_key=instance.course_id).first()
        course_title = modulestore().get_course(instance.course_id).display_name_with_default
        if course_bot:
            message = "I see you've enrolled to the *%s*. There is a bot [%s](https://telegram.me/%s?start=start)"\
                       " linked to the course, I recommend you to chat with him" %\
                       (course_title, course_bot.bot_name, course_bot.bot_name)
            bot.sendMessage(chat_id=telegram_user.telegram_id,
                            text=message,
                            parse_mode=telegram.ParseMode.MARKDOWN)

class EdxTelegramUser(models.Model):
    """
    Relations between edx telegram users
    """
    STATUS_NEW = 'new'
    STATUS_ACTIVE = 'active'
    STATUS_DONE = 'done'
    STATUSES = (
        (STATUS_NEW, 'New'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DONE, 'Done')
    )
    student = models.ForeignKey(User, db_index=True)
    hash = models.CharField(max_length=38, blank=True, null=True)
    telegram_id = models.CharField(max_length=10, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)
    status = models.CharField(max_length=6, choices=STATUSES, default=STATUS_NEW)

    def generate_hash(self):
        """
        generate key for authorization
        :return: string
        """
        str_to_hash = str(self.student.pk) + str(self.student.username) + str(self.modified)

        return hashlib.md5(str_to_hash).hexdigest()

    @staticmethod
    def post_save(sender, instance, created, **kwargs):
        """
        Method for post_save signal which creates a auth hash
        """
        if not instance.hash:
            instance.hash = instance.generate_hash()
            instance.save()


post_save.connect(EdxTelegramUser.post_save, sender=EdxTelegramUser, dispatch_uid='add_hash')


class TfidMatrixAllCourses(models.Model):
    """
    Storing Tfid matrix for all available courses
    """
    matrix = PickledObjectField()


class MatrixEdxCoursesId(models.Model):
    """
    Relations between index of course in Tfid matrix and course_key in edX
    """
    course_index = models.IntegerField()
    course_key = models.CharField(max_length=100)


class TfidUserVector(models.Model):
    """
    Prediction vector for particular user
    """
    telegram_user = models.OneToOneField(
        EdxTelegramUser,
        on_delete=models.CASCADE,
        primary_key=True, )
    vector = PickledObjectField()

    def __str__(self):
        return self.telegram_user.student.username


class PredictionForUser(models.Model):
    """
    Storing last predicted course for particular user until
    user give his reaction (agree or not agree) for prediction
    """
    telegram_user = models.OneToOneField(
        EdxTelegramUser,
        on_delete=models.CASCADE,
        primary_key=True, )
    prediction_course = models.CharField(max_length=100)

    def __str__(self):
        return self.telegram_user.student.username


class LearningPredictionForUser(models.Model):
    """
    Storing list of test courses for making prediction learning
    """
    telegram_user = models.OneToOneField(
        EdxTelegramUser,
        on_delete=models.CASCADE,
        primary_key=True, )
    prediction_list = models.CharField(max_length=30)

    def get_list(self):
        return json.loads(self.prediction_list)

    def save_list(self, list_to_save):
        self.prediction_list = str(list_to_save)
        self.save()

    def __str__(self):
        return self.telegram_user.student.username


class UserCourseProgress(models.Model):
    STATUS_START = 'start'
    STATUS_INFO = 'info'
    STATUS_TEST = 'test'
    STATUS_END = 'end'
    STATUSES = (
        (STATUS_START, 'Start'),
        (STATUS_INFO, 'Info'),
        (STATUS_TEST, 'Test'),
        (STATUS_END, 'end'),
    )

    telegram_user = models.ForeignKey(EdxTelegramUser)
    course_key = models.CharField(max_length=100)
    current_step_order = models.IntegerField(default=0)
    current_step_status = models.CharField(max_length=6, choices=STATUSES, default=STATUS_TEST)


class BotFriendlyCourses(models.Model):
    """
    List of courses which supports telegram bot
    """
    course_key = models.CharField(max_length=100, db_index=True)
    bot_name = models.CharField(max_length=64, blank=True, null=True)
