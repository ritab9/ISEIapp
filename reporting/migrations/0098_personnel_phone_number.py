# Generated by Django 3.2.6 on 2024-06-18 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0097_remove_personnel_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='personnel',
            name='phone_number',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
