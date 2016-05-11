# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0008_userlocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='botfriendlycourses',
            name='token',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
