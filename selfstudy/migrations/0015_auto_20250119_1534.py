# Generated by Django 3.2 on 2025-01-19 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0033_alter_level_level'),
        ('selfstudy', '0014_alter_indicatorevaluation_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardNarrative',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text1', models.TextField(blank=True, null=True)),
                ('text2', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='indicatorevaluation',
            name='score',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4)], null=True),
        ),
        migrations.CreateModel(
            name='StandardEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('narrative', models.TextField(blank=True, null=True)),
                ('average_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('selfstudy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='standard_evaluations', to='selfstudy.selfstudy')),
                ('standard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accreditation.standard')),
            ],
        ),
    ]
