# Generated by Django 3.2 on 2025-01-20 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0029_remove_actionplan_self_study'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actionplansteps',
            options={'ordering': ['action_plan', 'number']},
        ),
        migrations.AlterUniqueTogether(
            name='actionplansteps',
            unique_together={('action_plan', 'number')},
        ),
    ]
