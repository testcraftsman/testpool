# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0014_profile_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='action',
            field=models.CharField(default=b'none', max_length=36),
        ),
        migrations.AddField(
            model_name='profile',
            name='action_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 15, 6, 45, 24, 119189), auto_now_add=True),
            preserve_default=False,
        ),
    ]
