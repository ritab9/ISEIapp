# Generated by Django 3.2 on 2024-12-11 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0015_actionplandirective_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='apr',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='directive',
            name='progress_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apr.progressstatus'),
        ),
    ]