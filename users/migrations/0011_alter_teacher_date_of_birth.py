# Generated by Django 3.2 on 2021-08-01 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_teacher_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='date_of_birth',
            field=models.DateField(default='1975-01-01'),
            preserve_default=False,
        ),
    ]