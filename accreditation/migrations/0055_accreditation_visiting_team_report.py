# Generated by Django 5.2 on 2025-05-06 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0054_rename_indicatorscores_indicatorscore_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accreditation',
            name='visiting_team_report',
            field=models.URLField(blank=True, null=True),
        ),
    ]
