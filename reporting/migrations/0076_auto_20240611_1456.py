# Generated by Django 3.2.6 on 2024-06-11 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0075_auto_20240611_0750'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='educationalenrichmentactivity',
            unique_together={('day190', 'dates', 'type')},
        ),
        migrations.AlterUniqueTogether(
            name='sundayschooldays',
            unique_together={('day190', 'date')},
        ),
    ]
