# Generated by Django 3.2 on 2024-12-05 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0008_alter_apr_accreditation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionplansteps',
            name='number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
