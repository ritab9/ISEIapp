# Generated by Django 3.2 on 2025-01-27 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0026_auto_20250126_2112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selfstudy_teammember',
            name='active',
        ),
    ]
