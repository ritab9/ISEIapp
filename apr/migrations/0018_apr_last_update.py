# Generated by Django 3.2 on 2024-12-11 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0017_remove_apr_last_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='apr',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
