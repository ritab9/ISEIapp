# Generated by Django 3.2 on 2021-05-09 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_teacher_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='profile_picture',
            field=models.ImageField(blank=True, default='users/ProfilePictures/blank-profile.jpg', null=True, upload_to='users/ProfilePictures/'),
        ),
    ]
