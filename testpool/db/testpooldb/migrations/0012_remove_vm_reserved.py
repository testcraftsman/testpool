# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0011_auto_20161012_0615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vm',
            name='reserved',
        ),
    ]
