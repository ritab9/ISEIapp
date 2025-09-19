# accreditation/migrations/0058_populate_required_evidence.py
from django.db import migrations


def load_required_evidence(apps, schema_editor):
    Category = apps.get_model("accreditation", "RequiredEvidenceCategory")
    Evidence = apps.get_model("accreditation", "RequiredEvidence")

    data = {
        "General Documentation": [
            "Campus map and building layout",
            "Current year class schedule",
            "Current list of instructional equipment and supplies available",
            "Evidence of professional growth activities",
            "Last principal evaluation results",
            "Student roster (indicating gender, grade, ethnicity)",
            "Teacher professional growth plans",
            "Teacher observations (at least one for each teacher)",
        ],
        "Financial/Legal Information": [
            "Copy of driver’s license for all bus drivers (if applicable)",
            "Evidence of current school vehicle insurance",
            "Financial statement for the last full fiscal year",
            "Last financial review/audit report with the statement",
            "Monthly financial statements for the current school year",
            "Operating budget for current school year",
            "Organizational documents (business, 501(c)3, NGO) & bylaws",
        ],
        "Records": [
            "Board minutes for at least one year",
            "Copy of last fire Marshall inspection",
            "Copy of last fire alarm system inspection",
            "Copy of last cafeteria health inspection",
            "Drinking water approval by Health Dept.",
            "Faculty meeting minutes for current school year",
            "Maintenance & Safety Report for current school year",
            "Record of emergency drills (fire, tornado, etc)",
            "Standardized test results for the last 3-years",
        ],
        "Plans": [
            "Emergency Preparedness Plan (EPP)",
            "Safety Plan (if not included in EPP)",
            "Hazardous material management plan (asbestos, chemicals – lab/cleaning, etc)",
            "Marketing & Recruiting Plan",
            "Strategic Plan (long-range)",
            "Technology Plan (includes acceptable use policy for Internet)",
        ],
        "Policies/Procedures": [
            "Course outlines for each course (secondary)",
            "Contagious Disease Protocol",
            "Distance/online learning curriculum & policies (as applicable)",
            "Elementary curriculum map for each grade level",
            "School handbook/Student handbook",
            "Staff Handbook",
        ],
    }

    for category_name, evidences in data.items():
        category, _ = Category.objects.get_or_create(name=category_name)
        for ev in evidences:
            Evidence.objects.get_or_create(category=category, name=ev)


def unload_required_evidence(apps, schema_editor):
    """Reverse migration: delete the inserted records."""
    Category = apps.get_model("accreditation", "RequiredEvidenceCategory")
    Evidence = apps.get_model("accreditation", "RequiredEvidence")

    # delete evidence first (FK)
    Evidence.objects.all().delete()
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0057_requiredevidencecategory_requiredevidence'),
    ]

    operations = [
        migrations.RunPython(load_required_evidence, reverse_code=unload_required_evidence),
    ]
