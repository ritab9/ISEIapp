# Generated by Django 3.2 on 2025-01-16 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0031_alter_standard_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indicator',
            options={'ordering': ['standard', 'code']},
        ),
        migrations.AlterModelOptions(
            name='level',
            options={'ordering': ['-level']},
        ),
    ]
