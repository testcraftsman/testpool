# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0004_vmkvp'),
    ]

    operations = [
        migrations.AddField(
            model_name='vm',
            name='kvps',
            field=models.ManyToManyField(to='testpooldb.KVP', through='testpooldb.VMKVP'),
        ),
    ]
