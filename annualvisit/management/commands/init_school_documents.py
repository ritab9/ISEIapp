from django.core.management.base import BaseCommand
from users.models import School
from annualvisit.models import SchoolDocuments

class Command(BaseCommand):
    help = "Create a SchoolDocuments instance for each active school"

    def handle(self, *args, **kwargs):
        schools = School.objects.filter(active=True)
        created_count = 0
        skipped_count = 0

        for school in schools:
            obj, created = SchoolDocuments.objects.get_or_create(school=school)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created SchoolDocuments for {school.name}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Already exists for {school.name}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done! {created_count} created, {skipped_count} skipped."
        ))
