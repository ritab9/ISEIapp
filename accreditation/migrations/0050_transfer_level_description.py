from django.db import migrations


def transfer_met_description(apps, schema_editor):
    Indicator = apps.get_model('accreditation', 'Indicator')
    Level = apps.get_model('accreditation', 'Level')

    # Loop over all Indicators and transfer Met level description
    for indicator in Indicator.objects.all():
        # Find the Level with level=3 (Met) for this indicator
        met_level = Level.objects.filter(indicator=indicator, level=3).first()
        if met_level and met_level.description:
            indicator.met_description = met_level.description
            indicator.save()


class Migration(migrations.Migration):
    dependencies = [
        ('accreditation', '0049_indicator_met_description'),
    ]

    operations = [
        # Transfer the description for the Met level to the Indicator model
        migrations.RunPython(transfer_met_description),

    ]