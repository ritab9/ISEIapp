# Generated by Django 3.2 on 2021-08-17 01:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0058_auto_20210817_0114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tcertificate',
            old_name='note_isei',
            new_name='office_note',
        ),
        migrations.RenameField(
            model_name='tcertificate',
            old_name='note_teacher',
            new_name='public_note',
        ),
    ]