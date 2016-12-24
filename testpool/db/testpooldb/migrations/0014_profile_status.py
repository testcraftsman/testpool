# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0013_auto_20161103_0550'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]
