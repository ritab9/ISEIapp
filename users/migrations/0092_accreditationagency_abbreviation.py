# Generated by Django 3.2.6 on 2024-05-17 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0091_accreditationagency'),
    ]

    operations = [
        migrations.AddField(
            model_name='accreditationagency',
            name='abbreviation',
            field=models.CharField(default='ISEI', max_length=10),
            preserve_default=False,
        ),
    ]
