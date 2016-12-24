# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0016_exception'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exception',
            old_name='order',
            new_name='level',
        ),
    ]
