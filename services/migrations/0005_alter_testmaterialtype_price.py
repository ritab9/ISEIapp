# Generated by Django 3.2.6 on 2024-07-15 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_testmaterialtype_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testmaterialtype',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Price'),
        ),
    ]
