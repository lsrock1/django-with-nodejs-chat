# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-12 09:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=30)),
                ('total_money', models.IntegerField(default=0)),
                ('number', models.IntegerField()),
                ('is_now', models.BooleanField(default=0)),
            ],
        ),
    ]
