# Generated by Django 3.2 on 2024-07-17 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0125_auto_20240714_1256'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='annualreport',
            options={'ordering': ('school_year', 'school', 'report_type')},
        ),
    ]
