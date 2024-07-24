# Generated by Django 3.2.6 on 2024-07-12 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0122_auto_20240627_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='category',
            field=models.CharField(choices=[('B', 'Bible'), ('C', 'Computer/Tech'), ('F', 'Fine Arts'), ('L', 'Language Arts'), ('M', 'Math'), ('ML', 'Modern Language'), ('SC', 'Science'), ('SS', 'Social Studies'), ('V', 'Vocational Arts Courses'), ('W', 'Wellness/Health/PE'), ('E', 'Elementary'), ('MT', 'Mentorship')], max_length=50),
        ),
    ]