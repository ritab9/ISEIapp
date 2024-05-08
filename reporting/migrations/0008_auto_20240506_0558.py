# Generated by Django 3.2.6 on 2024-05-06 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0084_alter_country_name'),
        ('reporting', '0007_auto_20240506_0553'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ReportDueDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateField()),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.region')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reporting.report')),
            ],
            options={
                'verbose_name_plural': 'Report due dates',
            },
        ),
        migrations.DeleteModel(
            name='ReportDueDates',
        ),
    ]
