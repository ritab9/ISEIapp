# Generated by Django 3.2 on 2021-08-22 23:42

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0050_delete_teachercertificationapplication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='ssn',
            field=localflavor.us.models.USSocialSecurityNumberField(blank=True, max_length=11, null=True),
        ),
    ]
