# Generated by Django 3.2.6 on 2024-07-15 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_alter_testmaterialtype_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmaterialtype',
            name='update',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated'),
        ),
    ]
