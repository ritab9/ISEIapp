# Generated by Django 3.2.6 on 2024-05-07 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0017_alter_student_annual_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='county',
        ),
    ]