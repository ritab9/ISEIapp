# Generated by Django 5.2 on 2025-06-11 19:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0061_financialtwoyeardataentry_current_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentFollowUpDataKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('level', models.CharField(choices=[('elementary', 'Elementary'), ('secondary', 'Secondary')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='StudentFollowUPDataEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('two_years_ago', models.SmallIntegerField(blank=True, null=True, verbose_name='2 Years Ago')),
                ('one_year_ago', models.SmallIntegerField(blank=True, null=True, verbose_name='1 Year Ago')),
                ('school_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followup_data', to='selfstudy.schoolprofile')),
                ('followup_data_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='selfstudy.studentfollowupdatakey')),
            ],
        ),
    ]
