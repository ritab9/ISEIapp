# Generated by Django 3.2.6 on 2024-06-11 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0071_reporttype_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='SundaySchoolDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('RC', 'Regular Classes'), ('FT', 'Field Trip'), ('MT', 'Mission Trip'), ('SL', 'Service Learning'), ('MU', 'Music Trip'), ('OT', 'Other Education Enrichment Activity'), ('ST', 'Standardized Testing'), ('GR', 'Graduation')], default='RC', max_length=2)),
                ('day190', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sunday_school_days', to='reporting.day190')),
            ],
        ),
        migrations.CreateModel(
            name='EducationalEnrichmentActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('FT', 'Field Trip'), ('MT', 'Mission Trip'), ('SL', 'Service Learning'), ('MU', 'Music Trip'), ('OT', 'Other Education Enrichment Activity')], default='FT', max_length=2)),
                ('dates', models.CharField(max_length=255)),
                ('no_school_days', models.PositiveIntegerField()),
                ('day190', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educational_enrichment_activities', to='reporting.day190')),
            ],
        ),
    ]
