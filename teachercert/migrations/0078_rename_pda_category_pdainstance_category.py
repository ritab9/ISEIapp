# Generated by Django 3.2.6 on 2021-08-25 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0077_alter_pdatype_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pdainstance',
            old_name='pda_category',
            new_name='category',
        ),
    ]
