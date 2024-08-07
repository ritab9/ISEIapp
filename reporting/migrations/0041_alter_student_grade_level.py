# Generated by Django 3.2.6 on 2024-05-16 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0040_alter_student_grade_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='grade_level',
            field=models.IntegerField(choices=[(-2, 'Pre-K'), (-1, 'K'), (0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')]),
        ),
    ]
