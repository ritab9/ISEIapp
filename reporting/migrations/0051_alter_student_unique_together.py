# Generated by Django 3.2.6 on 2024-05-19 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0050_reporttype_view_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='student',
            unique_together={('name', 'birth_date', 'annual_report')},
        ),
    ]
