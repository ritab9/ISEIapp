# Generated by Django 3.2.6 on 2024-05-20 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0052_alter_student_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='baptized',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', '-')], default='U', max_length=1),
        ),
        migrations.AlterField(
            model_name='student',
            name='parent_sda',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('U', '-')], default='U', max_length=1, verbose_name='Parent SDA'),
        ),
    ]
