# Generated by Django 3.2.6 on 2021-08-24 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0064_rename_fee_paid_teachercertificationapplication_billed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='principal_letter',
            field=models.CharField(choices=[('y', 'Yes'), ('n', 'No'), ('a', 'N/A')], default='a', max_length=1, verbose_name='Letter of Recommendation from Principal has been sent (for Designated )'),
        ),
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='resume',
            field=models.CharField(choices=[('y', 'Yes'), ('n', 'No'), ('a', 'N/A')], default='a', max_length=1, verbose_name='Verification of experience (for Designated or Vocational)'),
        ),
    ]