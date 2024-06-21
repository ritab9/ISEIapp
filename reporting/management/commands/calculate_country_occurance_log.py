from django.core.management.base import BaseCommand
from users.models import Country
from math import ceil, log10


class Command(BaseCommand):
    help = "Update student_occurrence_log based on student_occurrence."

    def handle(self, *args, **kwargs):
        for country in Country.objects.all():
            # Protect against log10(0)
            if country.student_occurrence > 0:
                new_log = ceil(log10(country.student_occurrence))
            else:
                new_log = 0

            if country.student_occurrence_log != new_log:
                country.student_occurrence_log = new_log
                country.save()
                self.stdout.write(f"Updated log for country: {country.name}")
