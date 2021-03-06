# Generated by Django 3.2 on 2021-07-30 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20210714_0838'),
        ('teachercert', '0042_certification_renewal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField()),
                ('renewal_date', models.DateField()),
                ('renewal_requirements', models.CharField(max_length=100)),
                ('certification_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teachercert.certificationtype')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherEndorsement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teachercert.certificate')),
                ('endorsement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teachercert.endorsement')),
            ],
        ),
        migrations.DeleteModel(
            name='Certification',
        ),
    ]
