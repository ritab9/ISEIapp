# Generated by Django 3.2.6 on 2024-06-26 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0120_auto_20240626_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closing',
            name='grade_count',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='closing', to='reporting.gradecount'),
        ),
    ]
