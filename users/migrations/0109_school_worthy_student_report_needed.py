# Generated by Django 3.2 on 2024-11-12 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0108_school_initial_accreditation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='worthy_student_report_needed',
            field=models.BooleanField(default=False),
        ),
    ]