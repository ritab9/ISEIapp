from datetime import timezone
from django.utils import timezone as dj_timezone

from django.db import models
from users.models import School, SchoolType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class InfoPage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)  # For easy lookup, e.g. "accreditation-intro"
    content = models.TextField()
    def __str__(self):
        return self.name

class AccreditationApplication(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    lowest_grade = models.CharField(max_length=5)
    current_highest_grade = models.CharField(max_length=5)
    planned_highest_grade = models.CharField(max_length=5)

    anticipated_accreditation = models.CharField(verbose_name=_('Anticipated School Year for Accreditation Site Visit'), max_length=10, blank=True)
    signature = models.CharField(max_length=30)
    date = models.DateField(default=dj_timezone.now)

    ss_orientation_date = models.DateField(blank=True, null=True, verbose_name="SelfStudy Orientation Date")
    site_visit_start_date=models.DateField(blank=True, null=True)
    site_visit_end_date=models.DateField(blank=True, null=True)
    def __str__(self):
        return f"Accreditation Application: + {self.school}"

    def visit_date_range(self):
        """ Returns a formatted string for the visit date range, ensuring the month is not repeated if both dates are in the same month."""
        if not self.site_visit_start_date or not self.site_visit_end_date:
            return "-"
        start_date = self.site_visit_start_date
        end_date = self.site_visit_end_date
        if start_date.strftime("%B") == end_date.strftime("%B"):
            return f"{start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%B %d')}-{end_date.strftime('%B %d, %Y')}"

class AccreditationTerm(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=60)
    description = models.TextField()
    def __str__(self):
        return self.code + " " + self.name

class Accreditation(models.Model):
    class AccreditationStatus(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')  # Accreditation process is scheduled
        ACTIVE = 'active', _('Active')  # The accreditation is currently active
        PAST = 'past', _('Past')  # The accreditation is no longer active

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    visit_start_date = models.DateField(null=True, blank=True)
    visit_end_date = models.DateField(null=True, blank=True)
    term = models.ForeignKey(AccreditationTerm, on_delete=models.CASCADE, null=True, blank=True)
    term_start_date = models.DateField(null=True, blank=True)
    term_end_date = models.DateField(null=True, blank=True)
    term_comment = models.TextField(null=True, blank=True, verbose_name=_('Comment'))
    coa_approval_date = models.DateField(null=True, blank=True, verbose_name="COA Approval Date")
    status = models.CharField(
        max_length=20,
        choices=AccreditationStatus.choices,
        default=AccreditationStatus.SCHEDULED
    )
    previous_self_study_link = models.URLField(null=True, blank=True)

    def visit_date_range(self):
        """ Returns a formatted string for the visit date range, ensuring the month is not repeated if both dates are in the same month."""
        if not self.visit_start_date or not self.visit_end_date:
            return ""
        start_date = self.visit_start_date
        end_date = self.visit_end_date
        if start_date.strftime("%B") == end_date.strftime("%B"):
            return f"{start_date.strftime('%B %d')}-{end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%B %d')}-{end_date.strftime('%B %d, %Y')}"

    def __str__(self):
        if self.term_end_date and self.term_start_date:
            return f"Accreditation: School {self.school}, {self.visit_date_range()}"
        else:
            return f"Accreditation: School {self.school} in Works"

    def save(self, *args, **kwargs):
        # Ensure only one active accreditation per school
        if self.status == Accreditation.AccreditationStatus.ACTIVE:
            Accreditation.objects.filter(
                school=self.school,
                status=Accreditation.AccreditationStatus.ACTIVE
            ).exclude(pk=self.pk).update(status=Accreditation.AccreditationStatus.PAST)

        super().save(*args, **kwargs)

#Standards Models (to be used for SelfStudy)
class StandardManager(models.Manager):
    def top_level(self):
        # Exclude substandards by filtering out those with a parent_standard
        return self.filter(parent_standard__isnull=True)

class Standard(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    evidence = models.TextField(blank=True, null=True)

    parent_standard = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, blank=True, null=True,
        related_name='substandards'
    )
    objects = StandardManager()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.number}. {self.name}"

class Indicator(models.Model):
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    code = models.CharField(max_length=7)
    key_word=models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField()
    school_type = models.ForeignKey(SchoolType, on_delete=models.CASCADE, default=5)
    version = models.CharField(max_length=10, default = "2.0 (2005)")
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['standard', 'code', 'version']]
        ordering = ['standard', 'code']

    def __str__(self):
        return f"{self.code}"

class Level(models.Model):
    LEVEL_CHOICES = (
        (1, 'Not Met (1)'),
        (2, 'Partially Met (2)'),
        (3, 'Met (3)'),
        (4, 'Exceptional (4)'),
    )
    level = models.IntegerField(choices=LEVEL_CHOICES)
    description = models.TextField(blank=True)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-level']
    def __str__(self):
        return self.get_level_display()

