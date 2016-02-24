# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningPredictionForUser',
            fields=[
                ('telegram_user', models.OneToOneField(primary_key=True, serialize=False, to='edx_telegram_bot.EdxTelegramUser')),
                ('prediction_list', models.CharField(max_length=30)),
            ],
        ),
        migrations.RenameModel(
            old_name='TfidUserMatrix',
            new_name='TfidUserVector',
        ),
        migrations.RenameField(
            model_name='tfiduservector',
            old_name='matrix',
            new_name='vector',
        ),
    ]
