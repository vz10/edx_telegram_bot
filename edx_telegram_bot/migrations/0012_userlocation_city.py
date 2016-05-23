# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0011_edxtelegramuser_telegram_nick'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlocation',
            name='city',
            field=models.CharField(max_length=30, blank=True),
        ),
    ]
