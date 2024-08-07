# Generated by Django 3.2.6 on 2024-05-08 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0030_alter_student_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='location',
            field=models.CharField(blank=True, choices=[('on-site', 'On-Site'), ('satelite', 'Satelite'), ('distance-learning', 'Distance-Learning')], default=None, max_length=20, null=True),
        ),
    ]
