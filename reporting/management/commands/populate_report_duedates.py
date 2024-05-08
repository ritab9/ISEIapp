from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from users.models import Region
from reporting.models import ReportType, ReportDueDate


class Command(BaseCommand):
    help = 'Populate the Report and ReportingDueDate models'

    def handle(self, *args, **options):
        # a dictionary representing our data
        data = {
            'Americas': {
                'Opening Data Report': '2024-08-01',
                'Employee Data Report': '2024-08-01',
                'Student Enrollment Report': '2024-08-01',
                '190 - Day Report': '2024-08-01',
                'In-Service Year End Report': '2024-06-01',
                'Annual Progress Report (APR)': '2024-05-01'
            },
            'Europe': {
                'Opening Data Report': '2024-09-20',
                'Employee Data Report': '2024-09-20',
                'Student Enrollment Report': '2024-09-20',
                '190 - Day Report': '2024-09-20',
                'In-Service Year End Report': '2024-06-01',
                'Annual Progress Report (APR)': '2024-05-01'
            },
            'Asia': {
                'Opening Data Report': '2024-10-31',
                'Employee Data Report': '2024-10-31',
                'Student Enrollment Report': '2024-10-31',
                '190 - Day Report': '2024-10-31',
                'In-Service Year End Report': '2024-06-01',
                'Annual Progress Report (APR)': '2024-05-01'
            },
        }

        report_names = {report for reports in data.values() for report in reports.keys()}
        report_objs = {report: ReportType.objects.get_or_create(name=report)[0] for report in report_names}

        for region_name, reports in data.items():
            region = Region.objects.get(name=region_name)
            for report_name, due_date in reports.items():
                report, _ = ReportType.objects.get_or_create(name=report_name)
                due_date = parse_date(due_date)
                ReportDueDate.objects.create(region=region, report=report, due_date=due_date)

        self.stdout.write(self.style.SUCCESS('Successfully populated the Report and ReportingDueDate models'))
