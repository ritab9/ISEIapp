# Generated by Django 5.2 on 2025-04-30 15:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0054_alter_standardizedtestsession_test_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhilantrophyProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('development_program', models.TextField(blank=True, null=True)),
                ('school_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='philantrophy_program', to='selfstudy.schoolprofile')),
            ],
        ),
        migrations.CreateModel(
            name='SupportService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_advisement', models.TextField(blank=True, null=True)),
                ('career_advisement', models.TextField(blank=True, null=True)),
                ('personal_counseling', models.TextField(blank=True, null=True)),
                ('school_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_services', to='selfstudy.schoolprofile')),
            ],
        ),
    ]
