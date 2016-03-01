import hashlib
import json

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from opaque_keys.edx.locator import CourseLocator
from picklefield.fields import PickledObjectField
from xmodule.modulestore.django import modulestore


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

        return "hash::" + hashlib.md5(str_to_hash).hexdigest()

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
    STATUSES = (
        (STATUS_START, 'Start'),
        (STATUS_INFO, 'Info'),
        (STATUS_TEST, 'Test')
    )

    telegram_user = models.ForeignKey(EdxTelegramUser)
    course_key = models.CharField(max_length=100)
    current_step_order = models.IntegerField(default=0)
    current_step_status = models.CharField(max_length=6, choices=STATUSES, default=STATUS_START)

class BotFriendlyCourses(models.Model):
    """
    List of courses which supports telegram bot
    """
    course_list = []

    # def __init__(self, *args, **kwargs):
    #     super(BotFriendlyCourses, self).__init__(*args, **kwargs)
    #     results = modulestore().get_courses()
    #     course_list = [(str(course), str(course)) for course in results if course.scope_ids.block_type == 'course']
    #     self._meta.fields[1].choices = course_list

    course_key = models.CharField(max_length=100, choices=[(1, 1), (2, 2)])
