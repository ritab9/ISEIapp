# Generated by Django 3.2 on 2025-01-13 16:41

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0026_alter_indicator_version'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accreditation',
            name='current_accreditation',
        ),
        migrations.AddField(
            model_name='accreditation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accreditation',
            name='status',
            field=models.CharField(choices=[('in_works', 'In Works'), ('current', 'Current'), ('retired', 'Retired')], default='current', max_length=20),
        ),
        migrations.AddField(
            model_name='accreditation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
