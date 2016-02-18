import hashlib

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


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
    hash = models.CharField(max_length=36, blank=True, null=True)
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

        return "hash" + hashlib.md5(str_to_hash).hexdigest()

    def post_save(self, sender, instance, created, **kwargs):
        """
        Method for post_save signal which creates a auth hash
        """
        if created and not instance.hash_key:
            instance.hash_key = self.generate_hash()
            instance.save()


post_save.connect(EdxTelegramUser.post_save, EdxTelegramUser, dispatch_uid='add_hash')
