from django.core.management.base import BaseCommand
from users.models import Address, StateField
from django.db import transaction

class Command(BaseCommand):
    help = 'Migrates state_old data to state_us field'

    def handle(self, *args, **options):

        # Get all instances of Address
        addresses = Address.objects.all()

        # We can form a list of state codes from the choices defined in StateField
        state_codes = [code for code, _ in StateField().choices]

        # Start transaction
        with transaction.atomic():
            for address in addresses:
                if not address.state_us and address.state_old:
                    # Check if state_old is a valid state code in the list we formed
                    if address.state_old in state_codes:
                        # If a valid state code found, set state_us to this code and save the instance
                        address.state_us = address.state_old
                        address.save()

        self.stdout.write