# Generated by Django 3.2.6 on 2024-06-26 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0116_auto_20240626_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='opening',
            name='grade_count',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opening', to='reporting.gradecount'),
        ),
    ]
