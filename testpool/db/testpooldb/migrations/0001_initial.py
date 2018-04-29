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
                ('connection', models.CharField(max_length=128)),
                ('product', models.CharField(max_length=128)),
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
                ('resource_max', models.IntegerField(default=1)),
                ('expiration', models.IntegerField(default=600)),
                ('status', models.IntegerField(default=1)),
                ('action', models.CharField(default=b'none', max_length=36)),
                ('action_time', models.DateTimeField(auto_now_add=True)),
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
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('status', models.IntegerField(default=2)),
                ('ip_addr', models.CharField(max_length=16, null=True, blank=True)),
                ('action', models.CharField(default=b'clone', max_length=36)),
                ('action_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceKVP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kvp', models.ForeignKey(to='testpooldb.KVP')),
                ('vm', models.ForeignKey(to='testpooldb.Resource')),
            ],
        ),
        migrations.CreateModel(
            name='Traceback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(default=0, null=True)),
                ('file_name', models.CharField(max_length=128, null=True)),
                ('lineno', models.IntegerField(default=0, null=True)),
                ('func_name', models.CharField(max_length=32, null=True)),
                ('text', models.CharField(max_length=128)),
                ('profile', models.ForeignKey(to='testpooldb.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='resource',
            name='kvps',
            field=models.ManyToManyField(to='testpooldb.KVP', through='testpooldb.ResourceKVP'),
        ),
        migrations.AddField(
            model_name='resource',
            name='profile',
            field=models.ForeignKey(to='testpooldb.Profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='kvps',
            field=models.ManyToManyField(to='testpooldb.KVP', through='testpooldb.ProfileKVP'),
        ),
    ]
