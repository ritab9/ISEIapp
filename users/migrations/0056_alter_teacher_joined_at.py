# Generated by Django 3.2.6 on 2021-09-01 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0055_alter_teacher_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='joined_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
