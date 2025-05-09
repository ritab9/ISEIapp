# Generated by Django 3.2 on 2025-01-14 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0030_auto_20250114_1527'),
        ('selfstudy', '0005_alter_selfstudy_last_updated'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField()),
                ('reference_documents', models.TextField(blank=True, null=True)),
                ('explanation', models.TextField(blank=True, null=True)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='accreditation.indicator')),
                ('self_study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicator_evaluations', to='selfstudy.selfstudy')),
            ],
            options={
                'unique_together': {('self_study', 'indicator')},
            },
        ),
    ]
