# Generated by Django 3.2 on 2025-02-02 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0116_alter_schooltype_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='school',
            old_name='type',
            new_name='grade_levels',
        ),
        migrations.AddField(
            model_name='school',
            name='school_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.schooltype'),
        ),
    ]
