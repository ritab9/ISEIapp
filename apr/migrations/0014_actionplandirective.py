# Generated by Django 3.2 on 2024-12-10 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0013_auto_20241210_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionPLanDirective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('completed_date', models.DateField(blank=True, null=True)),
                ('apr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apr.apr')),
            ],
        ),
    ]