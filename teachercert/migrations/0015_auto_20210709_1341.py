# Generated by Django 3.2 on 2021-07-09 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0014_auto_20210709_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdainstance',
            name='amount',
            field=models.DecimalField(decimal_places=1, max_digits=3),
        ),
        migrations.AlterField(
            model_name='pdainstance',
            name='units',
            field=models.CharField(choices=[('c', 'CEUs'), ('h', 'Clock Hours'), ('d', 'Days'), ('p', 'Pages')], max_length=1),
        ),
    ]
