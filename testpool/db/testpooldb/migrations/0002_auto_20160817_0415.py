# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vm',
            name='expiration',
            field=models.IntegerField(default=600),
        ),
        migrations.AlterField(
            model_name='vm',
            name='reserved',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
