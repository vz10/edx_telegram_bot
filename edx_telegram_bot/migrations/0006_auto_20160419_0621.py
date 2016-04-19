# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0005_auto_20160415_0712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourseprogress',
            name='current_step_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='usercourseprogress',
            name='current_step_status',
            field=models.CharField(default=b'test', max_length=6, choices=[(b'start', b'Start'), (b'info', b'Info'), (b'test', b'Test'), (b'end', b'end')]),
        ),
    ]
