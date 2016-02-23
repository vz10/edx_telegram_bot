# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx-telegram-bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edxtelegramuser',
            name='student',
        ),
        migrations.DeleteModel(
            name='TfidMatrixAllCourses',
        ),
        migrations.RemoveField(
            model_name='tfidstudentrmatrix',
            name='student',
        ),
        migrations.DeleteModel(
            name='EdxTelegramUser',
        ),
        migrations.DeleteModel(
            name='TfidStudentrMatrix',
        ),
    ]
