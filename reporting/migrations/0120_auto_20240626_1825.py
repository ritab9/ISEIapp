# Generated by Django 3.2.6 on 2024-06-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0119_rename_withdrew_count_closing_withdraw_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='closing',
            name='evangelistic_meeting_locations',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Location of Evangelistic Meetings'),
        ),
        migrations.AddField(
            model_name='closing',
            name='final_school_day',
            field=models.DateField(blank=True, null=True, verbose_name='Final date school was in full session (last academic schoolday'),
        ),
        migrations.AddField(
            model_name='closing',
            name='mission_trip_locations',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Location of Mission trips'),
        ),
        migrations.AddField(
            model_name='closing',
            name='no_mission_trips',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Number of Mission trips your students participated in'),
        ),
        migrations.AddField(
            model_name='closing',
            name='no_mission_trips_school',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Number of Mission trips planned or executed by your school'),
        ),
        migrations.AddField(
            model_name='closing',
            name='student_baptism_non_sda_parent',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Student Baptised with non-SDA parent(s)'),
        ),
        migrations.AddField(
            model_name='closing',
            name='student_baptism_sda_parent',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Student Baptised during the past 12 months (SDA parent(s))'),
        ),
        migrations.AddField(
            model_name='closing',
            name='student_evangelistic_meetings_baptism',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Total number of baptisms as a result of student evangelism (student baptisms should not be counted in this category.)'),
        ),
        migrations.AddField(
            model_name='closing',
            name='student_lead_evangelistic_meetings',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Number of Student Lead Evangelistic Meetings'),
        ),
    ]
