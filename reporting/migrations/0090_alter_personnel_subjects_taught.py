# Generated by Django 3.2.6 on 2024-06-14 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0089_alter_personnel_subjects_taught'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='subjects_taught',
            field=models.ManyToManyField(blank=True, to='reporting.Subject'),
        ),
    ]
