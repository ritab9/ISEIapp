# Generated by Django 3.2 on 2024-12-17 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0010_auto_20241217_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indicator',
            name='description_at_level',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='levels',
        ),
        migrations.AddField(
            model_name='level',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='level',
            name='indicator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accreditation.indicator'),
            preserve_default=False,
        ),
    ]
