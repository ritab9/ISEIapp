# Generated by Django 3.2 on 2025-01-31 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0036_alter_accreditation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='accreditation',
            name='term_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
