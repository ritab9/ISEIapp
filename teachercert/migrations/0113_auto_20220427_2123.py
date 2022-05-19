# Generated by Django 3.2.6 on 2022-04-27 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0112_auto_20220427_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardchecklist',
            name='assessment',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Educational Assessment'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_health',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Health (recommended)'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_language',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Language Arts'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_math',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Mathematics'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_reading',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Reading'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_religion',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Religion'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_science',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Science'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='em_social',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Elementary Methods in Social Studies (recommended)'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='exceptional_child',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Exceptional Child in the Classroom'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='other_ed_credit',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Other Professional Education Credits'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='psychology',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Developmental and Educational Psychology'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='sda_education',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Principles and Philosophy of SDA Education'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='sec_methods',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Secondary Curriculum and Methods'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='sec_rw_methods',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Secondary Reading and Writing Methods (recommended)'),
        ),
        migrations.AlterField(
            model_name='standardchecklist',
            name='technology',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Technology in Teaching & Learning'),
        ),
    ]