# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0010_auto_20161006_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vm',
            name='status',
            field=models.IntegerField(default=2),
        ),
    ]
