# Generated by Django 3.2.6 on 2024-06-23 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0101_opening'),
    ]

    operations = [
        migrations.AddField(
            model_name='personnel',
            name='sda',
            field=models.BooleanField(default=True),
        ),
    ]
