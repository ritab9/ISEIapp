# Generated by Django 3.2.6 on 2021-09-01 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0056_alter_teacher_joined_at'),
        ('teachercert', '0086_alter_teacherbasicrequirement_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicclass',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher'),
        ),
        migrations.AlterField(
            model_name='ceuinstance',
            name='ceu_report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teachercert.ceureport'),
        ),
        migrations.AlterField(
            model_name='ceureport',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher'),
        ),
        migrations.AlterField(
            model_name='ceutype',
            name='ceu_category',
            field=models.ForeignKey(help_text='Choose a category', on_delete=django.db.models.deletion.CASCADE, to='teachercert.ceucategory'),
        ),
        migrations.AlterField(
            model_name='tcertificate',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher'),
        ),
    ]