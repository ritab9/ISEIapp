# Generated by Django 5.2 on 2025-04-30 05:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0049_alter_standardizedtestsession_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeLevelTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_level', models.CharField(max_length=50)),
                ('test_administered', models.TextField()),
                ('achievement_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grade_level_tests', to='selfstudy.studentachievementdata')),
            ],
        ),
        migrations.DeleteModel(
            name='StandardizedTestList',
        ),
    ]
