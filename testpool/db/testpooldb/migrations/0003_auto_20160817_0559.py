# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0002_auto_20160817_0415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vm',
            name='expiration',
        ),
        migrations.AddField(
            model_name='profile',
            name='expiration',
            field=models.IntegerField(default=600),
        ),
    ]
