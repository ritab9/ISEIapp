# Generated by Django 3.2.6 on 2024-06-16 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0093_alter_staffposition_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffposition',
            name='category',
            field=models.CharField(choices=[('A', 'Administrative'), ('T', 'Teaching'), ('G', 'General_Staff')], max_length=50),
        ),
    ]