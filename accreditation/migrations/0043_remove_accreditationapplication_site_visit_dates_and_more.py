# Generated by Django 5.2 on 2025-04-20 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0042_accreditationapplication_signature_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accreditationapplication',
            name='site_visit_dates',
        ),
        migrations.AddField(
            model_name='accreditationapplication',
            name='site_visit_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='accreditationapplication',
            name='site_visit_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
