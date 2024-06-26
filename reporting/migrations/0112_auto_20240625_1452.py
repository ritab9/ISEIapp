# Generated by Django 3.2.6 on 2024-06-25 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0111_auto_20240625_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='degree',
            name='rank',
            field=models.PositiveIntegerField(choices=[(1, 'Associate'), (2, 'Bachelor'), (3, 'Masters'), (4, 'Doctorate'), (5, 'Professional')], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='personneldegree',
            name='degree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personnel_degrees', to='reporting.degree'),
        ),
    ]
