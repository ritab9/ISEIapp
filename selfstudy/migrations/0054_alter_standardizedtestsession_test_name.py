# Generated by Django 5.2 on 2025-04-30 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0053_alter_standardizedtestscore_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardizedtestsession',
            name='test_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
