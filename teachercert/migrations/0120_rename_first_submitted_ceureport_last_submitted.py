# Generated by Django 3.2.6 on 2022-05-18 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0119_ceureport_first_submitted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ceureport',
            old_name='first_submitted',
            new_name='last_submitted',
        ),
    ]
