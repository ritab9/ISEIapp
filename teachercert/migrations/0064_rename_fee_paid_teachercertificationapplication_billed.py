# Generated by Django 3.2.6 on 2021-08-24 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0063_teachercertificationapplication_isei_revision_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teachercertificationapplication',
            old_name='fee_paid',
            new_name='billed',
        ),
    ]
