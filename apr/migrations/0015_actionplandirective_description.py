# Generated by Django 3.2 on 2024-12-10 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0014_actionplandirective'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionplandirective',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
