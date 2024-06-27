# Generated by Django 3.2.6 on 2024-06-23 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0105_alter_student_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opening',
            old_name='BA_count',
            new_name='associate_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='MA_count',
            new_name='bachelor_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='PhD_count',
            new_name='doctorate_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_0_end_count',
            new_name='masters_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_10_end_count',
            new_name='previous_year_grade_0_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_11_end_count',
            new_name='previous_year_grade_10_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_12_end_count',
            new_name='previous_year_grade_11_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_1_end_count',
            new_name='previous_year_grade_12_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_2_end_count',
            new_name='previous_year_grade_1_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_3_end_count',
            new_name='previous_year_grade_2_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_4_end_count',
            new_name='previous_year_grade_3_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_5_end_count',
            new_name='previous_year_grade_4_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_6_end_count',
            new_name='previous_year_grade_5_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_7_end_count',
            new_name='previous_year_grade_6_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_8_end_count',
            new_name='previous_year_grade_7_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='grade_9_end_count',
            new_name='previous_year_grade_8_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='k_end_count',
            new_name='previous_year_grade_9_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='less_BA_count',
            new_name='previous_year_k_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='pre_k_end_count',
            new_name='previous_year_pre_k_end_count',
        ),
        migrations.RenameField(
            model_name='opening',
            old_name='withdrawn_count',
            new_name='previous_year_withdraw_count',
        ),
    ]