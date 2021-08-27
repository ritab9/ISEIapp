# Generated by Django 3.2 on 2021-08-19 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_alter_teacher_ssn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collegeattended',
            name='college',
        ),
        migrations.AddField(
            model_name='collegeattended',
            name='address',
            field=models.CharField(default='', max_length=40, verbose_name='City, Country'),
        ),
        migrations.AddField(
            model_name='collegeattended',
            name='name',
            field=models.CharField(default='college name', max_length=30, verbose_name='College Name'),
        ),
        migrations.AlterField(
            model_name='schoolofemployment',
            name='address',
            field=models.CharField(default='', max_length=40, verbose_name='City, Country'),
        ),
    ]