# Generated by Django 3.2 on 2021-08-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0060_academicclass_credits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tcertificate',
            name='renewal_requirements',
            field=models.CharField(max_length=400),
        ),
    ]