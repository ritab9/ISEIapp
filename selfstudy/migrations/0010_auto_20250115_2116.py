# Generated by Django 3.2 on 2025-01-15 21:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0009_auto_20250115_0153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialadditionaldataentries',
            old_name='other_financial_data',
            new_name='key',
        ),
        migrations.RenameField(
            model_name='financialadditionaldataentries',
            old_name='response',
            new_name='value',
        ),
        migrations.RenameField(
            model_name='financialtwoyeardataentries',
            old_name='financial_data_category',
            new_name='key',
        ),
        migrations.RemoveField(
            model_name='schoolprofile',
            name='financial_2year_data',
        ),
        migrations.RemoveField(
            model_name='schoolprofile',
            name='financial_additional_data',
        ),
    ]
