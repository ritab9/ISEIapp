# Generated by Django 3.2 on 2024-12-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0021_actionplansteps_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionplansteps',
            name='completion_date',
            field=models.TextField(blank=True, null=True, verbose_name='Estimated Completion Date'),
        ),
    ]
