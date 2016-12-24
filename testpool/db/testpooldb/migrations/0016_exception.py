# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0015_auto_20161215_0645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exception',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('fname', models.CharField(max_length=128)),
                ('lineno', models.IntegerField(default=0)),
                ('fn', models.CharField(max_length=32)),
                ('text', models.CharField(max_length=128)),
                ('profile', models.ForeignKey(to='testpooldb.Profile')),
            ],
        ),
    ]
