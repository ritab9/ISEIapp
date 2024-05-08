from django.core.management.base import BaseCommand
from users.models import Country, Region
import requests


class Command(BaseCommand):
    help = 'Populate countries and regions'

    def handle(self, *args, **options):

        response = requests.get('https://restcountries.com/v3.1/all')
        countries_data = response.json()

        countries = []

        for country_data in countries_data:
            country = {
                'name': country_data['name']['common'],
                'code': country_data['cca2'],
                'region': country_data['region'],
            }
            countries.append(country)


        for country_data in countries:
            region_name = country_data['region']
            region, created = Region.objects.get_or_create(name=region_name)
            #region = Region.objects.get(name=country_data['region'])

            if not Country.objects.filter(name=country_data['name']).exists():
                Country.objects.create(name=country_data['name'], code=country_data['code'], region=region)
