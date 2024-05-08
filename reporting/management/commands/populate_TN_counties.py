from django.core.management.base import BaseCommand
from users.models import TNCounty


class Command(BaseCommand):
    help = 'Populate the TNCounty model'

    def handle(self, *args, **kwargs):
        counties = [
            "Anderson", "Bedford", "Benton", "Bledsoe", "Blount",
            "Bradley", "Campbell", "Cannon", "Carroll", "Carter",
            "Cheatham", "Chester", "Claiborne", "Clay", "Cocke",
            "Coffee", "Crockett", "Cumberland", "Davidson", "Decatur",
            "Dekalb", "Dickson", "Dyer", "Fayette", "Fentress",
            "Franklin", "Gibson", "Giles", "Grainger", "Greene",
            "Grundy", "Hamblen", "Hamilton", "Hancock", "Hardeman",
            "Hardin", "Hawkins", "Haywood", "Henderson", "Henry",
            "Hickman", "Houston", "Humphreys", "Jackson", "Jefferson",
            "Johnson", "Knox", "Lake", "Lauderdale", "Lawrence",
            "Lewis", "Lincoln", "Loudon", "McMinn", "McNairy",
            "Macon", "Madison", "Marion", "Marshall", "Maury",
            "Meigs", "Monroe", "Montgomery", "Moore", "Morgan",
            "Obion", "Overton", "Perry", "Pickett", "Polk",
            "Putnam", "Rhea", "Roane", "Robertson", "Rutherford",
            "Scott", "Sequatchie", "Sevier", "Shelby", "Smith",
            "Stewart", "Sullivan", "Sumner", "Tipton", "Trousdale",
            "Unicoi", "Union", "Van Buren", "Warren", "Washington",
            "Wayne", "Weakley", "White", "Williamson", "Wilson"
        ]

        for county_name in counties:
            TNCounty.objects.get_or_create(name=county_name)

        self.stdout.write(self.style.SUCCESS('Successfully populated TNCounty model'))
