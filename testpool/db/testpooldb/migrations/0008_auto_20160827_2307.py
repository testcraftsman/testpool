# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0007_auto_20160827_2256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vm',
            old_name='addr',
            new_name='ip_addr',
        ),
    ]
