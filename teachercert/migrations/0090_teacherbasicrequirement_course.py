# Generated by Django 3.2.6 on 2021-09-03 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0089_auto_20210901_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherbasicrequirement',
            name='course',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]