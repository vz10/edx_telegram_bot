# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edx_telegram_bot', '0014_usercourseprogress_xblock_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercourseprogress',
            name='xblock_key',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
