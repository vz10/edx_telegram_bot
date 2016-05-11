# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0007_auto_20160427_0408'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('telegram_user', models.ForeignKey(to='edx_telegram_bot.EdxTelegramUser')),
            ],
        ),
    ]
