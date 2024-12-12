# Generated by Django 3.2 on 2024-12-03 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apr', '0005_auto_20241203_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionplan',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actionplan',
            name='objective',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actionplan',
            name='standard',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ActionPlanSteps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('person_responsible', models.TextField(verbose_name='Person(s) Responsible')),
                ('action_steps', models.TextField(verbose_name='Action Steps')),
                ('timeline', models.TextField(verbose_name='Date/Timeline')),
                ('resources', models.TextField(verbose_name='Estimated Resources')),
                ('action_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apr.actionplan')),
            ],
        ),
    ]