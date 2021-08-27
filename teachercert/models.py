from django.db import models
from users.models import *
from django.core.validators import MinLengthValidator
import datetime
from datetime import datetime, date
import os


# Create your models here.


class SchoolYear(models.Model):
    name = models.CharField(max_length=9, unique=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    active_year = models.BooleanField(default=False)
    country = models.ManyToManyField(Country)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(SchoolYear, self).save(*args, **kwargs)
        if self.active_year:
            all = SchoolYear.objects.exclude(id=self.id).update(active_year=False)

class PDACategory(models.Model):
    name = models.CharField(max_length=25, null = False, blank=False)

    def __str__(self):
        return self.name

#PDA Report Modelst
class PDAType(models.Model):
    description = models.CharField(max_length=100, help_text='Describe the possible activities', null=False)
    evidence = models.CharField(max_length=100, help_text='What kind of evidence is expected for this type of activity', null=True, blank = True)
    pda_category = models.ForeignKey(PDACategory, on_delete=models.PROTECT, help_text="Choose a category", null=False, blank=False)
    ceu_value = models.CharField(max_length=60, null=True, blank=True)
    max_cap = models.CharField(max_length=30, null=True, blank = True)

    class Meta:
        ordering =('pda_category',)

    def __str__(self):
        return self.description


class PDAReport(models.Model):
    #timestamps for creation, update(save /teacher submission), and reviewed (by principal or ISEI)
    created_at = models.DateField(auto_now_add=True, blank = True)
    updated_at = models.DateField(auto_now=True, blank = True)
    reviewed_at = models.DateField(blank=True, null=True)

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

    def reading_ceu(self):
        reading_ceu = 0
        for i in self.pdainstance_set.all():
            if 'Reading' in i.pda_type.description:
                reading_ceu = reading_ceu+ i.suggested_ceu
        return round(reading_ceu,2)

    def travel_ceu(self):
        travel_ceu = 0
        for i in self.pdainstance_set.all():
            if 'Travel' in i.pda_type.description:
                travel_ceu = travel_ceu+ i.suggested_ceu
        return round(travel_ceu,2)

class PDAInstance(models.Model):
    # report contains teacher, school-year and summary

    # timestamps for creation, update(save /teacher submission), and reviewed (by principal or ISEI)
    created_at = models.DateField(auto_now_add=True, blank = True)
    updated_at = models.DateField(auto_now=True, blank = True)
    reviewed_at = models.DateField(blank=True, null=True)

    pda_report = models.ForeignKey(PDAReport, on_delete=models.PROTECT, null=False, blank=False)
    pda_category = models.ForeignKey(PDACategory, on_delete=models.PROTECT, null=True, blank=True)
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

    evidence = models.CharField(max_length=300, null=True, blank = True)
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
        ordering = ['pda_report']

    @property
    def suggested_ceu(self):
        if self.units == 'c':
            return self.amount
        elif self.units == 'p':
            return round(self.amount / 100, 2)
        elif self.units == 'h':
            return round(self.amount / 10, 2)
        elif self.units == 'd':
            return round(self.amount / 2, 2)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.description





class AcademicClass(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, null=False, blank=False)
    university = models.CharField(max_length=50, blank=False)
    name = models.CharField(max_length=50, blank=False)
    date_completed = models.DateField(blank=False)
    transcript_requested = models.BooleanField(default=False)
    transcript_received = models.BooleanField(default=False)
    credits = models.PositiveSmallIntegerField(blank= False, null=False)

    def __str__(self):
        return self.name

class EmailMessage(models.Model):
    name = models.CharField(max_length=50)
    message = models.CharField(max_length=200)

    def __str__(self):
        return self.name


#General Certification Information Models

class CertificationType(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=1000, null=True, blank=True)
    years_valid = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.name

class Requirement(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=600, null=True, blank=True)
    CATEGORIES = (
        ('g', 'General'),
        ('b', 'Basic'),
        ('o', 'Other'),
    )
    category = models.CharField(max_length=1, choices=CATEGORIES, help_text="Choose a category", null=False)
    certification_type = models.ManyToManyField(CertificationType)
    def __str__(self):
        return self.name

class Renewal(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=600, null=True, blank=True)
    certification_type = models.ManyToManyField(CertificationType)
        #models.ForeignKey(CertificationType, on_delete=models.PROTECT, null=False, blank=False)
    def __str__(self):
        return self.name

class Endorsement(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=600, null=True, blank=True)
    def __str__(self):
        return self.name

class ElementaryMethod(models.Model):
    name = models.CharField(max_length=30)
    required = models.BooleanField(default=True)
    def __str__(self):
        return self.name


#Teacher Certificates Models

class TCertificate(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, null=False, blank=False)
    certification_type = models.ForeignKey(CertificationType, on_delete=models.PROTECT, null=False, blank=False)
    issue_date = models.DateField(null=False, blank=False)
    renewal_date = models.DateField(null=False, blank=False)
    renewal_requirements = models.CharField(max_length = 400, null=False, blank=False)
    archived = models.BooleanField (default = False)
    public_note = models.CharField(max_length = 100, null=True, blank=True)
    office_note = models.CharField(max_length=100, null=True, blank=True)

    def expired(self):
        return self.renewal_date <= date.today()

    class Meta:
        unique_together = ['teacher','certification_type', 'issue_date' ]

    def __str__(self):
        return self.teacher.name() + "-" + self.certification_type.name

class TEndorsement(models.Model):
    certificate = models.ForeignKey(TCertificate, on_delete=models.CASCADE, null=False, blank=False)
    endorsement = models.ForeignKey(Endorsement, on_delete=models.PROTECT, null=False, blank=False)
    def __str__(self):
        return self.endorsement.name


class TeacherCertificationApplication(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    initial = models.BooleanField(default= True)
    CLEVELS = (
        ('v', 'Vocational'),
        ('s', "Secondary"),
        ('e', "Elementary"),
        ('d', 'Designated'),
    )
    cert_level = models.CharField(max_length=1, choices=CLEVELS, verbose_name="Certification Level Requested", null=True, blank=True)
    ELEVELS = (
        ('e', 'Elementary'),
        ('s', 'Secondary Area(s)'),
    )
    endors_level = models.CharField(max_length=1, choices=ELEVELS, verbose_name="Endorsement Level Requested", null=True, blank=True)
    courses_taught = models.CharField(max_length=50, blank=True, verbose_name="Courses Taught")
    #CHOICES=( ('y', 'Yes'), ('n','No'),('a', 'N/A'),)
    #resume = models.CharField(max_length= 1, choices = CHOICES, verbose_name = "Verification of experience (for Designated or Vocational)", default ='a')
    resume_file = models.FileField(upload_to='Applications/Resumes/%Y/%m/%d', null=True, blank=True)
    #principal_letter = models.CharField(max_length= 1, choices = CHOICES, verbose_name = "Letter of Recommendation from Principal has been sent (for Designated )", default ='a')
    principal_letter_file = models.FileField(upload_to='Applications/Principal Letters/%Y/%m/%d', null=True, blank=True)

    felony = models.BooleanField(verbose_name = "Check if you have ever been convicted of a felony (including a suspended sentence).",
                                 default= False)
    felony_description =models.CharField( max_length = 300, blank=True, null= True, verbose_name = "If yes, please describe")
    sexual_offence = models.BooleanField(
        verbose_name="Check if you have ever been under investigation for any sexual offense (excluding any charges which were fully cleared).",
        default=False)
    sexual_offence_description = models.CharField(max_length=300, blank=True, null=True, verbose_name="If yes, please describe")

    signature = models.CharField(verbose_name= "Applicant's signature", max_length=50, blank= False, null = False,)
    date = models.DateField(null=False, blank=False)

    #Office use section
    #date created
    date_received = models.DateField(auto_now_add=True, blank = True, null = True)
    billed = models.BooleanField(default = False, blank = False, null = False)
    public_note = models.CharField(max_length=255, blank=True, null=True)
    isei_note = models.CharField(max_length=255, blank=True, null=True)
    isei_revision_date = models.DateField(blank = True, null = True)
    closed = models.BooleanField(default=False, blank=False, null=False)

    def principal_letter_filename(self):
        return os.path.basename(self.principal_letter_file.name)

    def resume_filename(self):
        return os.path.basename(self.resume_file.name)
