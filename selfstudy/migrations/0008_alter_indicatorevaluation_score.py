# Generated by Django 3.2 on 2025-01-14 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0007_auto_20250114_2100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorevaluation',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Not Met'), (2, 'Partially Met'), (3, 'Met'), (4, 'Exceptional')], null=True),
        ),
    ]
