# Generated by Django 3.2.6 on 2021-09-15 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0095_tendorsement_range'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='cert_level',
            field=models.CharField(blank=True, choices=[('v', 'Vocational'), ('s', 'Subject Areas'), ('e', 'Elementary'), ('d', 'Designated')], max_length=1, null=True, verbose_name='Certification Level Requested'),
        ),
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='endors_level',
            field=models.CharField(blank=True, choices=[('e', 'Elementary'), ('s', 'Subject Area(s)')], max_length=1, null=True, verbose_name='Endorsement Level Requested'),
        ),
    ]
