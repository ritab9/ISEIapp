# Generated by Django 3.2.6 on 2021-09-01 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0059_auto_20210901_1718'),
        ('teachercert', '0088_teachercertificationapplication_date_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teachercertificationapplication',
            name='date_received',
        ),
        migrations.RemoveField(
            model_name='teachercertificationapplication',
            name='initial',
        ),
        migrations.AlterField(
            model_name='teachercertificationapplication',
            name='teacher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.teacher'),
        ),
    ]