# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0018_auto_20161223_2212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='traceback',
            old_name='fname',
            new_name='file_name',
        ),
        migrations.RenameField(
            model_name='traceback',
            old_name='fn',
            new_name='func_name',
        ),
    ]
