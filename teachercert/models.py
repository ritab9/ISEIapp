from django.db import models
from users.models import Teacher
from django.core.validators import MinLengthValidator
import datetime
# Create your models here.

class PDAType(models.Model):
    description = models.CharField(max_length=100, help_text='Describe the possible activities', null=False)
    evidence = models.CharField(max_length=50, help_text='What kind of evidence is expected for this type of activity', null=True, blank = True)
    CATEGORIES = (
        ('i', 'Independent'),
        ('g', 'Group'),
        ('c', 'Collaboration'),
        ('p', 'Presentation & Writing'),
    )
    category = models.CharField(max_length=1, choices=CATEGORIES, help_text="Choose a category", null=False)
    ceu_value = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        if self.evidence:
            ev = self.evidence
        else:
            ev=""
        return self.get_category_display() + ' - ' + self.description + '(' + ev + ')'


class SchoolYear(models.Model):
    name = models.CharField(max_length=9, unique=True)
    active_year = models.BooleanField(default=False)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(SchoolYear, self).save(*args, **kwargs)
        if self.active_year:
            all = SchoolYear.objects.exclude(id=self.id).update(active_year=False)


class PDARecord(models.Model):
    created_at = models.DateField(auto_now_add=True, blank = True)
    updated_at = models.DateField(auto_now=True, blank = True)
    # entered by teacher at object creation
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, null=True, blank=True, on_delete=models.PROTECT)
    date_submitted = models.DateField(null=True, blank=True)
    CHOICES = (
        ('n', 'Not yet reviewed'),
        ('a', 'Approved'),
        ('d', 'Denied'),
    )

    principal_reviewed = models.CharField(max_length= 1, choices= CHOICES, null=False, default='n')
    principal_comment = models.CharField(max_length=500, null=True, blank=True)

    isei_reviewed = models.CharField(max_length= 1, choices= CHOICES, null=False, default='n')
    isei_comment = models.CharField(max_length=500, null=True, blank=True)
    class Meta:
        unique_together = ('teacher', 'school_year',)
        ordering = ['school_year']

    # entered by teacher at object finalization
    summary = models.CharField(validators=[MinLengthValidator(1)], max_length=6000, blank=True, null=True)

    def approved_ceu(self):
        approved_ceu=0
        for i in self.pdainstance_set.all():
            if i.approved_ceu:
                approved_ceu=approved_ceu+i.approved_ceu
        return approved_ceu


class PDAInstance(models.Model):
    # record contains teacher, school-year and summary
    created_at = models.DateTimeField(auto_now_add=True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, blank = True)

    pda_record = models.ForeignKey(PDARecord, on_delete=models.PROTECT, null=False, blank=False)
    pda_type = models.ForeignKey(PDAType, on_delete=models.PROTECT, null=False, blank=False)
    date_completed = models.DateField(null=False)
    description = models.CharField(validators=[MinLengthValidator(1)], max_length=3000, blank=False, null=False)

    UNIT_CHOICES = (
        ('c', 'CEUs'),
        ('h', 'Clock Hours'),
        ('d', 'Days'),
        ('p', 'Pages'),
    )
    units = models.CharField(max_length=1, choices=UNIT_CHOICES, null=False, blank = False)
    amount = models.DecimalField(max_digits=5, decimal_places=1, null=False, blank = False)

    file = models.FileField(upload_to='Supporting_Files/%Y/%m/%d', null=True, blank=True)

    #used only for individual resubmission
    date_resubmitted = models.DateField(null=True, blank=True)
    REVIEW_CHOICES = (
        ('n', 'Not yet reviewed'),
        ('a', 'Approved'),
        ('d', 'Denied'),
    )
    principal_reviewed = models.CharField(max_length=1, choices=REVIEW_CHOICES, null=False, default='n')
    principal_comment = models.CharField(max_length=300, null=True, blank=True)
    isei_reviewed = models.CharField(max_length=1, choices=REVIEW_CHOICES, null=False, default='n')
    isei_comment = models.CharField(max_length=300, null=True, blank=True)

    approved_ceu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


    class Meta:
        ordering = ['pda_record']

    @property
    def suggested_ceu(self):
        if self.units is 'c':
            return self.amount
        elif self.units is 'p':
            return round(self.amount / 100, 2)
        elif self.units is 'h':
            return round(self.amount / 10, 2)
        elif self.units is 'd':
            return ('')

    def __str__(self):
        return self.description
