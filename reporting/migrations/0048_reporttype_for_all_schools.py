# Generated by Django 3.2.6 on 2024-05-19 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0047_alter_annualreport_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporttype',
            name='for_all_schools',
            field=models.BooleanField(default=False),
        ),
    ]
