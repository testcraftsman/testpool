# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0003_auto_20160817_0559'),
    ]

    operations = [
        migrations.CreateModel(
            name='VMKVP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kvp', models.ForeignKey(to='testpooldb.KVP')),
                ('vm', models.ForeignKey(to='testpooldb.VM')),
            ],
        ),
    ]
