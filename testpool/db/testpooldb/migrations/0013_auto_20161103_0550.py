# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0012_remove_vm_reserved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hv',
            name='hostname',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='hv',
            name='product',
            field=models.CharField(max_length=128),
        ),
    ]
