# Generated by Django 3.2 on 2021-08-17 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_college_collegeattended'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='college',
            name='country',
        ),
        migrations.AddField(
            model_name='collegeattended',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.college'),
        ),
        migrations.AlterField(
            model_name='college',
            name='address',
            field=models.CharField(default='', max_length=40, verbose_name='City, State, Country'),
        ),
        migrations.AlterField(
            model_name='collegeattended',
            name='end_date',
            field=models.DateField(help_text='mm/dd/yyyy'),
        ),
        migrations.AlterField(
            model_name='collegeattended',
            name='start_date',
            field=models.DateField(help_text='mm/dd/yyyy'),
        ),
        migrations.CreateModel(
            name='SchoolOfEmployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.CharField(max_length=50, unique=True)),
                ('address', models.CharField(default='', max_length=40, verbose_name='City, State, Country')),
                ('start_date', models.DateField(help_text='mm/dd/yyyy')),
                ('end_date', models.DateField(help_text='mm/dd/yyyy')),
                ('courses', models.CharField(default='', max_length=100, verbose_name='Courses taught')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_level', models.CharField(blank=True, choices=[('v', 'Vocational'), ('s', 'Secondary'), ('s', 'Elementary'), ('d', 'Designated')], max_length=1, null=True, verbose_name='Certification Level Requested')),
                ('endors_level', models.CharField(blank=True, choices=[('e', 'Elementary'), ('s', 'Secondary Subject Area(s)')], max_length=1, null=True, verbose_name='Endorsement Level Requested')),
                ('subject_areas', models.CharField(blank=True, help_text='Chemistry, Bible, Mathematics', max_length=50, verbose_name='Subject Areas')),
                ('transcripts_requested', models.BooleanField(default=False, verbose_name='Official college transcripts have been requested')),
                ('resume', models.BooleanField(choices=[('y', 'Yes'), ('n', 'No'), ('a', 'N/A')], default='a', max_length=1, verbose_name='Resume of work/teaching experience is included (for Designated and Vocational)')),
                ('principal_letter', models.BooleanField(choices=[('y', 'Yes'), ('n', 'No'), ('a', 'N/A')], default='a', max_length=1, verbose_name='Letter of Recommendation from Principal has been sent (for Designated and Vocational)')),
                ('felony', models.BooleanField(default=False, verbose_name='Have you ever been convicted of a felony (including a suspended sentence)?')),
                ('felony_description', models.CharField(blank=True, max_length=300, null=True, verbose_name='If yes, please describe')),
                ('sexual_offence', models.BooleanField(default=False, verbose_name='Have you ever been under investigation for any sexual offense (excluding any charges which were fully cleared)?')),
                ('sexual_offence_description', models.CharField(blank=True, max_length=300, null=True, verbose_name='If yes, please describe')),
                ('signature', models.CharField(max_length=50, verbose_name="Applicant's signature")),
                ('date', models.DateField(help_text='mm/dd/yyyy')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher')),
            ],
        ),
    ]
