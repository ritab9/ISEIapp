# Generated by Django 3.2 on 2025-02-04 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0037_auto_20250204_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolprofile',
            name='fte_student_ratio',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
