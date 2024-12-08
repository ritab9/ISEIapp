# Generated by Django 3.2 on 2024-12-03 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0004_auto_20241203_0103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apr',
            name='school_year',
        ),
        migrations.AddField(
            model_name='aprschoolyear',
            name='apr',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aprschoolyear', to='apr.apr'),
        ),
    ]
