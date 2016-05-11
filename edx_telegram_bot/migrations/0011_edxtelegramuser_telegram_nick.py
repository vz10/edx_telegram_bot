# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0010_auto_20160506_0128'),
    ]

    operations = [
        migrations.AddField(
            model_name='edxtelegramuser',
            name='telegram_nick',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
