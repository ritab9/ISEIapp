# Generated by Django 3.2 on 2025-01-17 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0013_alter_indicatorevaluation_reference_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatorevaluation',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, '1 (Not Met)'), (2, '2 (Partially Met)'), (3, '3 (Met)'), (4, '4 (Exceptional)')], null=True),
        ),
    ]
