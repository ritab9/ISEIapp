# Generated by Django 3.2 on 2021-07-30 23:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0046_rename_requirement_requirements'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EmailMessages',
            new_name='EmailMessage',
        ),
    ]