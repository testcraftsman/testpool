# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0008_auto_20160827_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vm',
            name='ip_addr',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='vm',
            name='profile',
            field=models.ForeignKey(to='testpooldb.Profile'),
        ),
        migrations.AlterField(
            model_name='vm',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]
