# Generated by Django 3.2.6 on 2024-05-02 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0122_auto_20220825_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolyear',
            name='current_school_year',
            field=models.BooleanField(default=False),
        ),
    ]