# Generated by Django 3.2 on 2025-01-15 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0010_auto_20250115_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialadditionaldatakey',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AddField(
            model_name='financialtwoyeardatakey',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
    ]
