# Generated by Django 3.2 on 2024-12-04 01:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0005_accreditation_term'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accreditation',
            old_name='end_date',
            new_name='term_end_date',
        ),
        migrations.RenameField(
            model_name='accreditation',
            old_name='start_date',
            new_name='term_start_date',
        ),
    ]
