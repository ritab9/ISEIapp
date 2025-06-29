# Generated by Django 5.2 on 2025-06-13 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0055_accreditation_visiting_team_report'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standard',
            options={'ordering': ['number']},
        ),
        migrations.AlterField(
            model_name='standard',
            name='number',
            field=models.DecimalField(decimal_places=1, max_digits=3, unique=True),
        ),
    ]
