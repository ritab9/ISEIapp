# Generated by Django 3.2 on 2021-08-22 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0048_auto_20210822_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachercertificationapplication',
            name='public_note',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='isei_note',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]