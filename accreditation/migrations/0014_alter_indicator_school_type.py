# Generated by Django 3.2 on 2024-12-17 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0013_auto_20241217_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='school_type',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='accreditation.schooltype'),
        ),
    ]