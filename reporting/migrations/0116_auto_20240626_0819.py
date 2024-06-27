# Generated by Django 3.2.6 on 2024-06-26 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0115_alter_opening_annual_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pre_k_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('k_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_0_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_1_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_2_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_3_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_4_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_5_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_6_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_7_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_8_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_9_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_10_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_11_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('grade_12_count', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_0_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_10_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_11_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_12_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_1_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_2_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_3_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_4_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_5_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_6_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_7_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_8_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='grade_9_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='k_count',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='opening_enrollment',
        ),
        migrations.RemoveField(
            model_name='opening',
            name='pre_k_count',
        ),
        migrations.CreateModel(
            name='Closing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('withdrew_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('annual_report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='closing', to='reporting.annualreport')),
                ('grade_count', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='closing', to='reporting.gradecount')),
            ],
        ),
    ]