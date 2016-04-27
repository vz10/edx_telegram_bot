# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0006_auto_20160419_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningpredictionforuser',
            name='prediction_list',
            field=models.TextField(blank=True),
        ),
    ]
