# Generated by Django 3.2 on 2021-08-13 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
