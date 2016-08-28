# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0005_vm_kvps'),
    ]

    operations = [
        migrations.AddField(
            model_name='vm',
            name='ip',
            field=models.CharField(default='127.0.0.1', max_length=16),
            preserve_default=False,
        ),
    ]
