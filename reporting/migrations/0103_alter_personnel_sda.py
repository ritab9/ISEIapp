# Generated by Django 3.2.6 on 2024-06-23 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0102_personnel_sda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='sda',
            field=models.BooleanField(default=True, verbose_name='SDA'),
        ),
    ]
