# Generated by Django 3.2 on 2025-01-09 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0024_alter_indicator_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standard',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
