# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0009_auto_20160930_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='vm',
            name='action',
            field=models.CharField(default=b'clone', max_length=36),
        ),
        migrations.AddField(
            model_name='vm',
            name='action_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 6, 5, 52, 11, 720041), auto_now_add=True),
            preserve_default=False,
        ),
    ]
