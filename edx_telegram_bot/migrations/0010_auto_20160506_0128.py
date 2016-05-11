# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0009_botfriendlycourses_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botfriendlycourses',
            name='token',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
