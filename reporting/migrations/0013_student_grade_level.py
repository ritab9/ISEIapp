# Generated by Django 3.2.6 on 2024-05-06 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0012_remove_student_grade_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='grade_level',
            field=models.CharField(choices=[('K', 'K'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], default=1, max_length=2),
            preserve_default=False,
        ),
    ]
