# Generated by Django 3.2 on 2021-08-18 21:33

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_teacher_ssn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='ssn',
            field=localflavor.us.models.USSocialSecurityNumberField(default='111-22-3333', max_length=11),
        ),
    ]