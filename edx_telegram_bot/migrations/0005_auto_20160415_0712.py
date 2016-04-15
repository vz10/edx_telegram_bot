# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0004_auto_20160301_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourseprogress',
            name='current_step_order',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='usercourseprogress',
            name='current_step_status',
            field=models.CharField(default=b'test', max_length=6, choices=[(b'start', b'Start'), (b'info', b'Info'), (b'test', b'Test')]),
        ),
    ]
