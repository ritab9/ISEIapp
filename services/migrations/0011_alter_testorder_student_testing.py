# Generated by Django 3.2.6 on 2024-07-15 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_auto_20240715_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testorder',
            name='student_testing',
            field=models.PositiveSmallIntegerField(verbose_name='Number of students testing'),
        ),
    ]
