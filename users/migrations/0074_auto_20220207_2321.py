# Generated by Django 3.2.6 on 2022-02-07 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_alter_teacher_joined_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='home_church',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='sda',
            field=models.BooleanField(default=True),
        ),
    ]
