# Generated by Django 3.2 on 2025-02-02 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0118_auto_20250202_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='school_type',
        ),
        migrations.AddField(
            model_name='school',
            name='school_type',
            field=models.ManyToManyField(blank=True, to='users.SchoolType', verbose_name='School Type'),
        ),
    ]
