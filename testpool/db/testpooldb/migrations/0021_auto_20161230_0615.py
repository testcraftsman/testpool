# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0020_auto_20161223_2249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hv',
            old_name='hostname',
            new_name='connection',
        ),
    ]
