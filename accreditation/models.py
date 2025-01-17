from datetime import timezone

from django.db import models
from users.models import School
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class AccreditationTerm(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=60)
    description = models.TextField()
    def __str__(self):
        return self.code + " " + self.name

class Accreditation(models.Model):
    class AccreditationStatus(models.TextChoices):
        IN_WORKS = 'in_works', _('In Works')  # Accreditation process is ongoing
        CURRENT = 'current', _('Current')    # The accreditation is currently valid
        RETIRED = 'retired', _('Retired')    # The accreditation is no longer active

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    visit_start_date = models.DateField(null=True, blank=True)
    visit_end_date = models.DateField(null=True, blank=True)
    term = models.ForeignKey(AccreditationTerm, on_delete=models.CASCADE, null=True, blank=True)
    term_start_date = models.DateField(null=True, blank=True)
    term_end_date = models.DateField(null=True, blank=True)
    coa_approval_date = models.DateField(null=True, blank=True, verbose_name="COA Approval Date")
    status = models.CharField(
        max_length=20,
        choices=AccreditationStatus.choices,
        default=AccreditationStatus.CURRENT
    )

    def __str__(self):
        return f"Accreditation: School {self.school}, {self.term_start_date.strftime('%Y')} - {self.term_end_date.strftime('%Y')}"

    def save(self, *args, **kwargs):
        # Ensure only one current accreditation per school
        if self.status == Accreditation.AccreditationStatus.CURRENT:
            Accreditation.objects.filter(
                school=self.school,
                status=Accreditation.AccreditationStatus.CURRENT
            ).exclude(pk=self.pk).update(status=Accreditation.AccreditationStatus.RETIRED)

        super().save(*args, **kwargs)

class StandardManager(models.Manager):
    def top_level(self):
        # Exclude substandards by filtering out those with a parent_standard
        return self.filter(parent_standard__isnull=True)

#Standards Models (to be used for SelfStudy)
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

class SchoolType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

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

