# Generated by Django 3.2 on 2025-01-09 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0025_alter_standard_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='version',
            field=models.CharField(default='2.0 (2005)', max_length=10),
        ),
    ]
