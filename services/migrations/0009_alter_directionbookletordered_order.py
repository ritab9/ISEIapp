# Generated by Django 3.2.6 on 2024-07-15 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_alter_testmaterialtype_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directionbookletordered',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='direction_booklets', to='services.testorder'),
        ),
    ]
