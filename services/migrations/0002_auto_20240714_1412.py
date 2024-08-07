# Generated by Django 3.2.6 on 2024-07-14 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerSheetOrdered',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(blank=True, choices=[(9, 'Grade 3, Level 9'), (10, 'Grade 4, Level 10'), (11, 'Grade 5, Level 11'), (12, 'Grade 6, Level 12'), (13, 'Grade 7, Level 13'), (14, 'Grade 8, Level 14'), (15, 'Grade 9, Level 15'), (16, 'Grade 10, Level 16'), (17, 'Grade 11-12, Level 17/18')], null=True, verbose_name='Level')),
                ('count', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Count')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_sheets', to='services.testorder')),
            ],
        ),
        migrations.CreateModel(
            name='DirectionBookletOrdered',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(blank=True, choices=[(1, 'Grades 3-8, Level 9-14'), (2, 'Grades 9-12 , Level 15-17/18')], null=True, verbose_name='Direction')),
                ('count', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Count')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='director_booklets', to='services.testorder')),
            ],
        ),
        migrations.CreateModel(
            name='ReusableTestBookletOrdered',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(blank=True, choices=[(9, 'Grade 3, Level 9'), (10, 'Grade 4, Level 10'), (11, 'Grade 5, Level 11'), (12, 'Grade 6, Level 12'), (13, 'Grade 7, Level 13'), (14, 'Grade 8, Level 14'), (15, 'Grade 9, Level 15'), (16, 'Grade 10, Level 16'), (17, 'Grade 11-12, Level 17/18')], null=True, verbose_name='Level')),
                ('count', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Count')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_booklets', to='services.testorder')),
            ],
        ),
        migrations.AlterField(
            model_name='testmaterialtype',
            name='name',
            field=models.IntegerField(choices=[(1, 'Reusable Test Booklet'), (2, 'Answer Sheet'), (3, 'Admin Directions Booklet'), (4, 'Test Scoring')]),
        ),
        migrations.DeleteModel(
            name='TestMaterialOrdered',
        ),
    ]
