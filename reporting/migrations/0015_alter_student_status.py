# Generated by Django 3.2.6 on 2024-05-07 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0014_alter_student_is_at_least_one_parent_sda'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('enrolled', 'Enrolled'), ('graduated', 'Graduated Last Year'), ('did_not_return', 'Did Not Return')], default='enrolled', max_length=15),
        ),
    ]