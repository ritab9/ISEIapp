# Generated by Django 3.2 on 2025-01-31 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0029_auto_20250130_2339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorevaluation',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(4, 4), (3, 3), (2, 2), (1, 1)], null=True),
        ),
    ]
