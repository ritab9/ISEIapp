# Generated by Django 3.2.6 on 2024-07-12 06:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0125_alter_schoolyear_sequence'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ceuinstance',
            options={'ordering': ['ceu_report', 'date_completed']},
        ),
    ]
