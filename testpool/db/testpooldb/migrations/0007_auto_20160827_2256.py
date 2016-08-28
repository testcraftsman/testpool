# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0006_vm_ip'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vm',
            old_name='ip',
            new_name='addr',
        ),
    ]
