# Generated by Django 3.2 on 2021-08-12 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_teacher_date_of_birth'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ('last_name',)},
        ),
    ]
