# Generated by Django 3.2.6 on 2024-06-12 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0078_remove_day190_number_of_sundays'),
    ]

    operations = [
        migrations.RenameField(
            model_name='educationalenrichmentactivity',
            old_name='no_school_days',
            new_name='days',
        ),
    ]
