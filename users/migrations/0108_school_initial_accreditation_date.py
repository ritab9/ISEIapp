# Generated by Django 3.2 on 2024-10-04 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0107_auto_20240908_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='initial_accreditation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]