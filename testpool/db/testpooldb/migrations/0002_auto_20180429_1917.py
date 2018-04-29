# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resourcekvp',
            old_name='vm',
            new_name='resource',
        ),
    ]
