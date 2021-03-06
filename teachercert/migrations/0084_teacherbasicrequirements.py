# Generated by Django 3.2.6 on 2021-08-31 22:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0055_alter_teacher_options'),
        ('teachercert', '0083_auto_20210830_1402'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherBasicRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('met', models.BooleanField(default=False)),
                ('basic_requirement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teachercert.requirement')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher')),
            ],
        ),
    ]
