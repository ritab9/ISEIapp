# Generated by Django 3.2 on 2025-02-02 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0115_schooltype'),
        ('accreditation', '0038_alter_accreditation_term_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='school_type',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='users.schooltype'),
        ),
        migrations.DeleteModel(
            name='SchoolType',
        ),
    ]
