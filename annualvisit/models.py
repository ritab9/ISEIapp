from django.db import models
from users.models import School
from teachercert.models import SchoolYear

class AnnualVisit(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="annual_visits")
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="annual_visits")
    visit_date = models.DateField(blank=True, null=True, help_text="Scheduled date of the visit.")
    representative = models.CharField(max_length=150, blank=True, null=True, help_text="Name of the ISEI representative who led the visit.")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        rep_name = self.representative if self.representative else "TBD"
        date_display = self.visit_date if self.visit_date else "Unscheduled"
        return f"Annual Visit - {self.school.name} ({date_display}) by {rep_name}"

class SchoolDocument(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="school_documents")
    link = models.URLField(blank=True, null=True, help_text="Google Drive folder link")
    first_accreditation_link = models.URLField(blank=True, null=True, help_text="Google Drive folder link - Accreditation Docs")

    def __str__(self):
        return f"Documents - {self.school.name}"