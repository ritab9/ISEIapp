# Generated by Django 3.2.6 on 2024-06-12 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0079_rename_no_school_days_educationalenrichmentactivity_days'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('annual_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reporting.annualreport')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('Administrative', 'Administrative'), ('Teaching', 'Teaching'), ('General Staff', 'General Staff')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('W', 'Wellness/Health/PE'), ('SC', 'Science'), ('L', 'Language Arts'), ('ML', 'Modern Language'), ('M', 'Math'), ('B', 'Bible'), ('SS', 'Social Studies'), ('C', 'Computer/Tech'), ('F', 'Fine Arts'), ('V', 'Vocational Arts Courses')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PersonnelPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reporting.personnel')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reporting.position')),
                ('subjects', models.ManyToManyField(to='reporting.Subject')),
            ],
        ),
        migrations.AddField(
            model_name='personnel',
            name='positions',
            field=models.ManyToManyField(through='reporting.PersonnelPosition', to='reporting.Position'),
        ),
    ]
