# Generated by Django 5.2 on 2025-04-20 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0041_infopage_accreditationapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='accreditationapplication',
            name='signature',
            field=models.CharField(default='sign here', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accreditationapplication',
            name='site_visit_dates',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
