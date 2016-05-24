# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0015_auto_20160519_1034'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramBot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bot_name', models.CharField(max_length=64, null=True, blank=True)),
                ('token', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='botfriendlycourses',
            name='bot_name',
        ),
        migrations.RemoveField(
            model_name='botfriendlycourses',
            name='token',
        ),
        migrations.AddField(
            model_name='botfriendlycourses',
            name='bot',
            field=models.ForeignKey(to='edx_telegram_bot.TelegramBot', null=True),
        ),
    ]
