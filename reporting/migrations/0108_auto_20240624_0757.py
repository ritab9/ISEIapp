# Generated by Django 3.2.6 on 2024-06-24 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0107_auto_20240624_0752'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opening',
            old_name='day_boy_count',
            new_name='boarding_boy_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='day_girl_count',
            new_name='boarding_girl_count',
        ),
    ]