# Generated by Django 3.2.6 on 2024-07-15 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_alter_directionbookletordered_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='testorder',
            name='student_testing',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Student testing'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='testorder',
            name='order_date',
            field=models.DateField(verbose_name='Order date'),
        ),
        migrations.AlterField(
            model_name='testorder',
            name='sub_total',
            field=models.PositiveSmallIntegerField(verbose_name='Sub total'),
        ),
        migrations.AlterField(
            model_name='testorder',
            name='testing_dates',
            field=models.CharField(max_length=255, verbose_name='Testing dates'),
        ),
    ]
