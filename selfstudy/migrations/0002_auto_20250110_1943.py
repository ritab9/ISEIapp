# Generated by Django 3.2 on 2025-01-10 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FinancialInformationEntries',
            new_name='Financial2YearDataEntries',
        ),
        migrations.RenameModel(
            old_name='FinancialData',
            new_name='Financial2YearDataKey',
        ),
        migrations.RenameModel(
            old_name='FinancialDataEntries',
            new_name='FinancialAdditionalDataEntries',
        ),
        migrations.RenameModel(
            old_name='FinancialInformationCategory',
            new_name='FinancialAdditionalDataKey',
        ),
        migrations.AlterModelOptions(
            name='financial2yeardatakey',
            options={'ordering': ['order_number']},
        ),
        migrations.AddField(
            model_name='schoolprofile',
            name='financial_2year_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='schoolprofile',
            name='financial_additional_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
