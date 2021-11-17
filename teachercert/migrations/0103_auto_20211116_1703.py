# Generated by Django 3.2.6 on 2021-11-16 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0102_alter_emailmessage_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='receiver',
            field=models.CharField(choices=[('t', 'Teacher'), ('p', 'Principal'), ('i', 'ISEI')], default='i', max_length=1),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='sender',
            field=models.CharField(choices=[('t', 'Teacher'), ('p', 'Principal'), ('i', 'ISEI')], default='i', max_length=1),
        ),
    ]
