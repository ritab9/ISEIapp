# Generated by Django 3.2.6 on 2021-09-15 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachercert', '0098_alter_tcertificate_public_note'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tcertificate',
            options={'ordering': ('-renewal_date',)},
        ),
    ]
