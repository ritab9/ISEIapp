# Generated by Django 3.2 on 2021-07-01 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0002_auto_20210630_1655'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pdarecord',
            old_name='isei_approved',
            new_name='isei_reviewed',
        ),
    ]
