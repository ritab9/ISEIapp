# Generated by Django 3.2.6 on 2024-05-28 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0061_auto_20240528_0738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abbreviateddays',
            old_name='dates',
            new_name='date',
        ),
    ]
