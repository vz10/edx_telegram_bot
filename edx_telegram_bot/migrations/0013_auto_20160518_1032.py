# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0012_userlocation_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercourseprogress',
            name='block_in_status',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usercourseprogress',
            name='grade_for_step',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='usercourseprogress',
            name='current_step_status',
            field=models.CharField(default=b'start', max_length=6, choices=[(b'start', b'Start'), (b'info', b'Info'), (b'test', b'Test'), (b'end', b'end')]),
        ),
    ]
