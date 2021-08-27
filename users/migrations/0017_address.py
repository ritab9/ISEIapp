# Generated by Django 3.2 on 2021-08-17 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_remove_teacher_current_certification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_1', models.CharField(max_length=128, verbose_name='address')),
                ('address_2', models.CharField(blank=True, max_length=128, verbose_name="address cont'd")),
                ('city', models.CharField(default='', max_length=64, verbose_name='city')),
                ('state', models.CharField(default='', max_length=4, verbose_name='state or province')),
                ('zip_code', models.CharField(default='', max_length=8, verbose_name='zip/postal code')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.country')),
            ],
        ),
    ]