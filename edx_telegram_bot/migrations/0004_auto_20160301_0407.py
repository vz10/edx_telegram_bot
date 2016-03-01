# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0003_auto_20160225_0937'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCourseProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_key', models.CharField(max_length=100)),
                ('current_step_order', models.IntegerField(default=0)),
                ('current_step_status', models.CharField(default=b'start', max_length=6, choices=[(b'start', b'Start'), (b'info', b'Info'), (b'test', b'Test')])),
                ('telegram_user', models.ForeignKey(to='edx_telegram_bot.EdxTelegramUser')),
            ],
        ),
        migrations.AlterField(
            model_name='botfriendlycourses',
            name='course_key',
            field=models.CharField(max_length=100, choices=[(1, 1), (2, 2)]),
        ),
    ]
