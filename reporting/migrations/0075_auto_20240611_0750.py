# Generated by Django 3.2.6 on 2024-06-11 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0074_rename_date_educationalenrichmentactivity_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalenrichmentactivity',
            name='type',
            field=models.CharField(choices=[(None, '--------------'), ('FT', 'Field Trip'), ('MT', 'Mission Trip'), ('SL', 'Service Learning'), ('MU', 'Music Trip'), ('OT', 'Other Education Enrichment Activity')], max_length=2),
        ),
        migrations.AlterField(
            model_name='sundayschooldays',
            name='type',
            field=models.CharField(choices=[(None, '--------------'), ('RC', 'Regular Classes'), ('FT', 'Field Trip'), ('MT', 'Mission Trip'), ('SL', 'Service Learning'), ('MU', 'Music Trip'), ('OT', 'Other Education Enrichment Activity'), ('ST', 'Standardized Testing'), ('GR', 'Graduation')], max_length=2),
        ),
    ]
