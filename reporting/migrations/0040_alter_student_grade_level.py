# Generated by Django 3.2.6 on 2024-05-15 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0039_student_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='grade_level',
            field=models.CharField(choices=[('Pre-K', 'Pre-K'), ('K', 'K'), ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], max_length=5),
        ),
    ]