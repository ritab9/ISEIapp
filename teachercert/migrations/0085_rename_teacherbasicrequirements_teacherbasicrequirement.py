# Generated by Django 3.2.6 on 2021-08-31 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0055_alter_teacher_options'),
        ('teachercert', '0084_teacherbasicrequirements'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TeacherBasicRequirements',
            new_name='TeacherBasicRequirement',
        ),
    ]
