# Generated by Django 3.2.6 on 2024-06-24 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0108_auto_20240624_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='opening',
            name='opening_enrollment',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
