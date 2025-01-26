# Generated by Django 3.2 on 2025-01-24 15:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0035_alter_accreditation_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('selfstudy', '0019_auto_20250124_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoordinatingTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='General Coordinating Team', max_length=255)),
                ('selfstudy', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coordinating_team', to='selfstudy.selfstudy')),
            ],
        ),
        migrations.CreateModel(
            name='StandardTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('selfstudy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='standard_teams', to='selfstudy.selfstudy')),
                ('standard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accreditation.standard')),
            ],
            options={
                'unique_together': {('selfstudy', 'name')},
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, help_text='Optional role of the member (e.g., Chair, Evaluator).', max_length=255, null=True)),
                ('coordinating_teams', models.ManyToManyField(blank=True, related_name='members', to='selfstudy.CoordinatingTeam')),
                ('standard_teams', models.ManyToManyField(blank=True, related_name='members', to='selfstudy.StandardTeam')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='team_member_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
