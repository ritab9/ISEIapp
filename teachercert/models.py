from django.db import models
from users.models import Teacher
from django.core.validators import MinLengthValidator
import datetime
# Create your models here.

class PDAType(models.Model):
    description = models.CharField(max_length=100, help_text='Describe the possible activities', null=False)
    evidence = models.CharField(max_length=50, help_text='What kind of evidence is expected for this type of activity', null=True)
    CATEGORIES = (
        ('i', 'Independent'),
        ('g', 'Group'),
        ('c', 'Collaboration'),
        ('p', 'Presentation & Writing'),
    )
    category = models.CharField(max_length=1, choices=CATEGORIES, help_text="Choose a category", null=False)
    ceu_value = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return self.get_category_display() + ' - ' + self.description


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
    created_at = models.DateTimeField(auto_now_add=True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, blank = True)
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
    principal_comment = models.CharField(max_length=300, null=True, blank=True)

    isei_reviewed = models.CharField(max_length= 1, choices= CHOICES, null=False, default='n')
    isei_comment = models.CharField(max_length=300, null=True, blank=True)
    class Meta:
        unique_together = ('teacher', 'school_year',)
        ordering = ['school_year']

    # entered by teacher at object finalization
    summary = models.CharField(validators=[MinLengthValidator(1)], max_length=3000, blank=True, null=True,
                               help_text='Summarize what you have learned from the combined activities and how you '
                                         'plan to apply this learning to your classroom')



class PDAInstance(models.Model):
    # record contains teacher, school-year and summary
    created_at = models.DateTimeField(auto_now_add=True, blank = True)
    updated_at = models.DateTimeField(auto_now=True, blank = True)

    pda_record = models.ForeignKey(PDARecord, on_delete=models.PROTECT, null=False, blank=False)
    pda_type = models.ForeignKey(PDAType, on_delete=models.PROTECT, null=False, blank=False)
    date_completed = models.DateField(null=False)
    description = models.CharField(validators=[MinLengthValidator(1)], max_length=3000, blank=False, null=False)

    # OR between those three
    ceu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    clock_hours = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    pages = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    file = models.FileField(upload_to='Supporting_Files/%Y/%m/%d', null=True, blank=True)

    #used only for individual resubmission
    date_submitted = models.DateField(null=True, blank=True)
    CHOICES = (
        ('n', 'Not yet reviewed'),
        ('a', 'Approved'),
        ('d', 'Denied'),
    )
    principal_reviewed = models.CharField(max_length=1, choices=CHOICES, null=False, default='n')
    principal_comment = models.CharField(max_length=300, null=True, blank=True)
    isei_reviewed = models.CharField(max_length=1, choices=CHOICES, null=False, default='n')
    isei_comment = models.CharField(max_length=300, null=True, blank=True)

    approved_ceu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


    class Meta:
        ordering = ['pda_record']

    @property
    def suggested_ceu(self):
        if self.ceu is not None:
            return self.ceu
        elif self.pages is not None:
            return round(self.pages / 100, 2)
        elif self.clock_hours is not None:
            return round(self.clock_hours / 10, 2)

    def __str__(self):
        return self.description
