# Generated by Django 3.2.6 on 2021-09-01 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0059_auto_20210901_1718'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ('last_name',)},
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='active',
        ),
    ]
