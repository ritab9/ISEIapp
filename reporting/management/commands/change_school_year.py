from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from teachercert.models import SchoolYear
from reporting.models import AnnualReport


class Command(BaseCommand):
    help = 'Change School Year for a given annual report - for testing purposes'

    def handle(self, *args, **kwargs):
        report_id = 6
        school_year_name = '2022-2023'

        try:
            report = AnnualReport.objects.get(id=report_id)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f'Annual Report with id {report_id} does not exist.'))
            return

        try:
            new_school_year = SchoolYear.objects.get(name=school_year_name)
            self.stdout.write(new_school_year.name)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f'School Year with name {school_year_name} does not exist.'))
            return

        report.school_year = new_school_year
        report.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated School Year for Annual Report {report_id}.'))
