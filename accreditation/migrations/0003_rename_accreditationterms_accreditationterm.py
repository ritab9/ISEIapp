# Generated by Django 3.2 on 2024-12-03 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0002_auto_20241203_2119'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AccreditationTerms',
            new_name='AccreditationTerm',
        ),
    ]
