# Generated by Django 3.2.6 on 2024-05-27 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0096_school_member'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='textapp',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
