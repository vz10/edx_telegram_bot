# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EdxTelegramUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(max_length=38, null=True, blank=True)),
                ('telegram_id', models.CharField(max_length=10, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', models.CharField(default=b'new', max_length=6, choices=[(b'new', b'New'), (b'active', b'Active'), (b'done', b'Done')])),
            ],
        ),
        migrations.CreateModel(
            name='MatrixEdxCoursesId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_index', models.IntegerField()),
                ('course_key', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TfidMatrixAllCourses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('matrix', picklefield.fields.PickledObjectField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='PredictionForUser',
            fields=[
                ('telegram_user', models.OneToOneField(primary_key=True, serialize=False, to='edx_telegram_bot.EdxTelegramUser')),
                ('prediction_course', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='TfidUserMatrix',
            fields=[
                ('telegram_user', models.OneToOneField(primary_key=True, serialize=False, to='edx_telegram_bot.EdxTelegramUser')),
                ('matrix', picklefield.fields.PickledObjectField(editable=False)),
            ],
        ),
        migrations.AddField(
            model_name='edxtelegramuser',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
