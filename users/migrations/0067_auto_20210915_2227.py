# Generated by Django 3.2.6 on 2021-09-15 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0066_alter_collegeattended_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collegeattended',
            name='end_date',
            field=models.CharField(help_text='yyyy', max_length=4),
        ),
        migrations.AlterField(
            model_name='collegeattended',
            name='start_date',
            field=models.CharField(help_text='yyyy', max_length=4),
        ),
    ]
