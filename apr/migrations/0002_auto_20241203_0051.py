# Generated by Django 3.2 on 2024-12-03 00:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0110_alter_school_abbreviation'),
        ('apr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APRSchoolYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='PriorityDirective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='apr',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.school'),
        ),
        migrations.AddField(
            model_name='directive',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='directive',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('apr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apr.apr')),
                ('progress_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apr.progressstatus')),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('action_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='apr.actionplan')),
                ('directive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='apr.directive')),
                ('priority_directive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='apr.prioritydirective')),
                ('recommendation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='apr.recommendation')),
                ('school_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='apr.aprschoolyear')),
            ],
        ),
        migrations.AddField(
            model_name='prioritydirective',
            name='apr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apr.apr'),
        ),
        migrations.AddField(
            model_name='prioritydirective',
            name='progress_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apr.progressstatus'),
        ),
        migrations.AddField(
            model_name='apr',
            name='year',
            field=models.ManyToManyField(to='apr.APRSchoolYear'),
        ),
    ]
