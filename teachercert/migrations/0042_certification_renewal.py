# Generated by Django 3.2 on 2021-07-30 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0041_auto_20210730_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='certification',
            name='renewal',
            field=models.CharField(default=' ', max_length=100),
            preserve_default=False,
        ),
    ]
