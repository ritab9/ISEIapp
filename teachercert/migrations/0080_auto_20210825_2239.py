# Generated by Django 3.2.6 on 2021-08-25 22:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0079_alter_pdainstance_pda_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pdainstance',
            old_name='category',
            new_name='pda_category',
        ),
        migrations.AlterField(
            model_name='pdainstance',
            name='pda_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teachercert.pdatype'),
        ),
    ]