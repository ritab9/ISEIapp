# Generated by Django 3.2 on 2024-08-18 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0128_alter_schoolyear_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicclass',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Course Name'),
        ),
    ]