# Generated by Django 3.2 on 2021-07-01 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_teacher_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
