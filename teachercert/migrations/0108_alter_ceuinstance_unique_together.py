# Generated by Django 3.2.6 on 2021-11-19 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0107_alter_teachercertificationapplication_billed'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ceuinstance',
            unique_together={('ceu_report', 'date_completed', 'description')},
        ),
    ]
