# Generated by Django 3.2 on 2021-08-19 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_alter_collegeattended_transcript_received'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schoolofemployment',
            old_name='school',
            new_name='name',
        ),
    ]
