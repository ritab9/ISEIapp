# Generated by Django 3.2 on 2021-08-17 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='address',
        ),
        migrations.RemoveField(
            model_name='school',
            name='country',
        ),
    ]