# Generated by Django 3.2 on 2025-01-30 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0028_auto_20250129_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialadditionaldatakey',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='financialtwoyeardatakey',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
