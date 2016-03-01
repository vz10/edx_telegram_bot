# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0002_auto_20160224_0329'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotFriendlyCourses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_key', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='predictionforuser',
            name='prediction_course',
            field=models.CharField(max_length=100),
        ),
    ]
