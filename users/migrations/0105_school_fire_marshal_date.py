# Generated by Django 3.2 on 2024-08-11 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0104_school_current_school_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='fire_marshal_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
