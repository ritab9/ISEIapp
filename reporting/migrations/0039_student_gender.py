# Generated by Django 3.2.6 on 2024-05-15 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0038_alter_student_age_at_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True),
        ),
    ]
