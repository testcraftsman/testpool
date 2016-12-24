# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testpooldb', '0017_auto_20161219_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='Traceback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(default=0)),
                ('fname', models.CharField(max_length=128)),
                ('lineno', models.IntegerField(default=0)),
                ('fn', models.CharField(max_length=32)),
                ('text', models.CharField(max_length=128)),
                ('profile', models.ForeignKey(to='testpooldb.Profile')),
            ],
        ),
        migrations.RemoveField(
            model_name='exception',
            name='profile',
        ),
        migrations.DeleteModel(
            name='Exception',
        ),
    ]
