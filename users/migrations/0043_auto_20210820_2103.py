# Generated by Django 3.2 on 2021-08-20 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_rename_school_schoolofemployment_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachercertificationapplication',
            name='date_received',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='teachercertificationapplication',
            name='fee_paid',
            field=models.BooleanField(default=False),
        ),
    ]