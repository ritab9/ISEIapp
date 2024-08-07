# Generated by Django 3.2 on 2021-08-17 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_address_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollegeAttended',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(help_text='mmm/dd/yyyy')),
                ('end_date', models.DateField(help_text='mmm/dd/yyyy')),
                ('level', models.CharField(choices=[('a', 'Associate degree'), ('b', "Bachelor's degree"), ('m', "Master's degree"), ('d', 'Doctoral degree')], help_text='Degree Level', max_length=1)),
                ('degree', models.CharField(help_text='BSc, Marketing & Psychology', max_length=40, verbose_name='Type, Degree Earned')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('address', models.CharField(default='', max_length=20, verbose_name='City, State')),
                ('country', models.ForeignKey(default='US', on_delete=django.db.models.deletion.CASCADE, to='users.country')),
            ],
        ),
    ]
