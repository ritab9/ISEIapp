# Generated by Django 3.2 on 2021-08-20 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0044_auto_20210820_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='date',
            field=models.DateField(),
        ),
    ]
