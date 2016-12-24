# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0019_auto_20161223_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traceback',
            name='file_name',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='traceback',
            name='func_name',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='traceback',
            name='level',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='traceback',
            name='lineno',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
