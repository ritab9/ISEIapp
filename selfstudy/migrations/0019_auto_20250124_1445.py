# Generated by Django 3.2 on 2025-01-24 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('selfstudy', '0018_auto_20250121_2354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='coordinating_team',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='standard',
        ),
        migrations.DeleteModel(
            name='CoordinatingTeam',
        ),
        migrations.DeleteModel(
            name='TeamMember',
        ),
    ]
