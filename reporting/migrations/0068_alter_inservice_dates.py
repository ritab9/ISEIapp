# Generated by Django 3.2.6 on 2024-06-04 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0067_inservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inservice',
            name='dates',
            field=models.CharField(max_length=255),
        ),
    ]