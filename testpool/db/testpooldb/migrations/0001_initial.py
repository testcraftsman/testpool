# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HV',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=128)),
                ('product', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(unique=True, max_length=128)),
                ('config_type', models.IntegerField(default=0, choices=[(0, b'ANY'), (1, b'STRICT')])),
            ],
        ),
        migrations.CreateModel(
            name='KVP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=128)),
                ('key', models.ForeignKey(to='testpooldb.Key')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('template_name', models.CharField(max_length=128)),
                ('vm_max', models.IntegerField(default=1)),
                ('hv', models.ForeignKey(to='testpooldb.HV')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileKVP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kvp', models.ForeignKey(to='testpooldb.KVP')),
                ('profile', models.ForeignKey(to='testpooldb.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('status', models.IntegerField(default=1, null=True, blank=True)),
                ('reserved', models.DateField(auto_now_add=True)),
                ('expiration', models.IntegerField(default=36000)),
                ('profile', models.ForeignKey(default=None, blank=True, to='testpooldb.Profile', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='kvps',
            field=models.ManyToManyField(to='testpooldb.KVP', through='testpooldb.ProfileKVP'),
        ),
    ]
