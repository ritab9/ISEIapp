# Generated by Django 3.2 on 2021-08-17 21:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_auto_20210817_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='school',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.school'),
        ),
    ]