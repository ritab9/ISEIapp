# Generated by Django 3.2.6 on 2024-05-28 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0059_alter_day190_inservice_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day190',
            name='end_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='day190',
            name='inservice_days',
            field=models.PositiveIntegerField(default=0, verbose_name='Inservice and Discretionary Days'),
        ),
        migrations.AlterField(
            model_name='day190',
            name='number_of_days',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='day190',
            name='number_of_sundays',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='day190',
            name='start_date',
            field=models.DateField(default=None),
        ),
    ]
