# Generated by Django 3.2.6 on 2024-05-20 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0095_auto_20240520_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='member',
            field=models.BooleanField(default=True),
        ),
    ]
