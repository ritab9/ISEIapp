from users.models import *
import os
from datetime import date, timedelta
from django.db.models import Q


from django.core.validators import MinLengthValidator


# Create your models here.


class SchoolYear(models.Model):
    name = models.CharField(max_length=9, unique=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    active_year = models.BooleanField(default=False)
    country = models.ManyToManyField(Country, blank=True)

    current_school_year = models.BooleanField(default=False)  # added field
    sequence = models.IntegerField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.current_school_year:
            # Set current_school_year for all other records to False
            SchoolYear.objects.filter(~Q(id=self.id)).update(current_school_year=False)
        super().save(*args, **kwargs)

    def get_next_school_year(self):
        try:
            return SchoolYear.objects.get(sequence=self.sequence + 1)
        except SchoolYear.DoesNotExist:
            return None

    def get_previous_school_year(self):
        try:
            return SchoolYear.objects.get(sequence=self.sequence - 1)
        except SchoolYear.DoesNotExist:
            return None

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return self.name


class CEUCategory(models.Model):
    name = models.CharField(max_length=25, null = False, blank=False, verbose_name = "CEU Category")

    def __str__(self):
        return self.name

#ceu Report Modelst
class CEUType(models.Model):
    description = models.CharField(max_length=100, help_text='Describe the possible activities', null=False, verbose_name = "CEU Type")
    evidence = models.CharField(max_length=100, help_text='What kind of evidence is expected for this type of activity', null=True, blank = True)
    ceu_category = models.ForeignKey(CEUCategory, on_delete=models.CASCADE, help_text="Choose a category", null=False, blank=False)
    ceu_value = models.CharField(max_length=60, null=True, blank=True)
    max_cap = models.CharField(max_length=30, null=True, blank = True)

    class Meta:
        ordering =('ceu_category',)

    def __str__(self):
        return self.description


class CEUReport(models.Model):
    #timestamps for creation, update(save /teacher submission), and reviewed (by principal or ISEI)
    created_at = models.DateField(auto_now_add=True, blank = True)
    updated_at = models.DateField(auto_now=True, blank = True)
    reviewed_at = models.DateField(blank=True, null=True)

    # entered by teacher at object creation
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, null=True, blank=True, on_delete=models.PROTECT)

    date_submitted = models.DateField(null=True, blank=True)
    last_submitted = models.DateField(blank=True, null=True)


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
        for i in self.ceuinstance_set.all():
            if i.approved_ceu:
                approved_ceu=approved_ceu+i.approved_ceu
        return approved_ceu

    def reading_ceu(self):
        reading_ceu = 0
        for i in self.ceuinstance_set.all():
            if 'Reading' in i.ceu_type.description:
                reading_ceu = reading_ceu+ i.suggested_ceu
        return round(reading_ceu,2)

    def travel_ceu(self):
        travel_ceu = 0
        for i in self.ceuinstance_set.all():
            if 'Travel' in i.ceu_type.description:
                travel_ceu = travel_ceu + i.suggested_ceu
        return round(travel_ceu,2)


    def __str__(self):
        return self.teacher.name() + ", " + self.school_year.name + " CEU Report"


class CEUInstance(models.Model):
    # report contains teacher, school-year and summary

    # timestamps for creation, update(save /teacher submission), and reviewed (by principal or ISEI)
    created_at = models.DateField(auto_now_add=True, blank = True)
    updated_at = models.DateField(auto_now=True, blank = True)
    reviewed_at = models.DateField(blank=True, null=True)

    ceu_report = models.ForeignKey(CEUReport, on_delete=models.CASCADE, null=False, blank=False)
    ceu_category = models.ForeignKey(CEUCategory, on_delete=models.PROTECT, null=True, blank=True)
    ceu_type = models.ForeignKey(CEUType, on_delete=models.PROTECT, null=False, blank=False)
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
        ordering = ['ceu_report', 'date_completed']
        unique_together = ['ceu_report','date_completed', 'description']

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
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    university = models.CharField(max_length=50, blank=False)
    name = models.CharField(max_length=50, blank=False)
    date_completed = models.DateField(blank=False)
    transcript_requested = models.BooleanField(default=False)
    transcript_received = models.BooleanField(default=False)
    credits = models.PositiveSmallIntegerField(blank= False, null=False)

    class Meta:
        ordering = ('-date_completed',)

    def __str__(self):
        return self.name

class EmailMessageTemplate(models.Model):
    CHOICES = (
        ('t', 'Teacher'),
        ('p', 'Principal'),
        ('i', 'ISEI'),
    )
    sender = models.CharField(max_length=1, choices=CHOICES, null=False, default='i')
    receiver = models.CharField(max_length=1, choices=CHOICES, null=False, default='i')
    name = models.CharField(max_length=50)
    message = models.CharField(max_length=300,)

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

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

class ElementaryMethod(models.Model):
    name = models.CharField(max_length=30)
    required = models.BooleanField(default=True)
    class Meta:
        ordering = ('name',)
    def __str__(self):
        return self.name


#Teacher Certificates Models

class TCertificate(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    certification_type = models.ForeignKey(CertificationType, on_delete=models.PROTECT, null=False, blank=False)
    issue_date = models.DateField(null=False, blank=False)
    renewal_date = models.DateField(null=False, blank=False)
    renewal_requirements = models.CharField(max_length = 400, null=False, blank=False)
    archived = models.BooleanField (default = False)
    public_note = models.CharField(max_length = 400, null=True, blank=True)
    office_note = models.CharField(max_length=100, null=True, blank=True)
    nad = models.BooleanField (default=False)

    def expired(self):
        return self.renewal_date <= date.today()

    class Meta:
        unique_together = ['teacher','certification_type', 'issue_date' ]
        ordering = ('-renewal_date',)

    def save(self, *args, **kwargs):
        super(TCertificate, self).save(*args, **kwargs)
        if not self.archived:
            all = TCertificate.objects.filter(teacher = self.teacher).exclude(id=self.id).update(archived=True)

    def __str__(self):
        return self.teacher.name() + "-" + self.certification_type.name


class TEndorsement(models.Model):
    certificate = models.ForeignKey(TCertificate, on_delete=models.CASCADE, null=False, blank=False)
    endorsement = models.ForeignKey(Endorsement, on_delete=models.PROTECT, null=False, blank=False)
    range = models.CharField(max_length=5, blank = True, null= True, default = "9-12")
    def __str__(self):
        return self.endorsement.name

class TeacherCertificationApplication(models.Model):
    date_initial = models.DateField(blank=True, null=True)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    CLEVELS = (
        ('v', 'Vocational'),
        ('s', "Subject Areas"),
        ('e', "Elementary"),
        ('d', 'Designated'),
    )
    cert_level = models.CharField(max_length=1, choices=CLEVELS, verbose_name="Certification Level Requested", null=True, blank=True)
    endors_level = models.CharField(max_length=5, verbose_name="Grade Range Requested", null=True, blank=True)
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
    CHOICES = (
        ('y', 'Billed'),
        ('n', "Not Billed"),
        ('z', "N/A"),
    )
    billed = models.CharField(max_length=1, choices=CHOICES, default = 'n')
    public_note = models.CharField(max_length=255, blank=True, null=True)
    isei_note = models.CharField(max_length=255, blank=True, null=True)
    isei_revision_date = models.DateField(blank = True, null = True)
    closed = models.BooleanField(default=False, blank=False, null=False)

    class Meta:
        ordering = ('billed','closed','date',)

    def expired(self):
        if self.isei_revision_date:
            if max(self.date, self.isei_revision_date) < date.today() - timedelta(days=183):
                return True
            else:
                return False
        else:
            return False

    def principal_letter_filename(self):
        return os.path.basename(self.principal_letter_file.name)

    def resume_filename(self):
        return os.path.basename(self.resume_file.name)


class TeacherBasicRequirement(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete= models.CASCADE, blank=False, null=False)
    basic_requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, blank=False, null=False)
    met = models.BooleanField(default=False)
    course = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        unique_together = ('teacher', 'basic_requirement')

    def __str__(self):
        return self.basic_requirement.name

class StandardChecklist(models.Model):
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=False, null=False,)
    sda=models.BooleanField(default=True, verbose_name= "SDA Church Member")
    #background_check = models.BooleanField(default=False, verbose_name= "Clean background check", blank= True, null=True)
    ba_degree = models.BooleanField(verbose_name="Baccalaureate degree or higher", blank= True, null=True)
    no_Ds = models.BooleanField(verbose_name = "No Grades below C- for required classes", blank= True, null=True)
    experience = models.BooleanField(verbose_name="3-years teaching experience", blank= True, null=True)

    sop = models.BooleanField(verbose_name="Spirit of Prophecy", default=False)
    sda_doctrine= models.BooleanField(verbose_name="SDA Doctrines", default=False)
    sda_history= models.BooleanField(verbose_name="SDA Church History", default=False)
    sda_health = models.BooleanField(verbose_name="SDA Health Principles", default=False)

    sda_education = models.PositiveSmallIntegerField(verbose_name="Principles and Philosophy of SDA Education",blank=True, null=True)
    psychology = models.PositiveSmallIntegerField(verbose_name="Educational Psychology",blank=True, null=True)
    dev_psychology =models.PositiveSmallIntegerField(verbose_name="Developmental Psychology (recommended)", blank=True, null=True)
    assessment = models.PositiveSmallIntegerField(verbose_name="Educational Assessment",blank=True, null=True)
    exceptional_child = models.PositiveSmallIntegerField(verbose_name="Exceptional Child in the Classroom",blank=True, null=True)
    technology = models.PositiveSmallIntegerField(verbose_name="Technology in Teaching & Learning",blank=True, null=True)

    sec_methods = models.PositiveSmallIntegerField(verbose_name="Secondary Curriculum and Methods", blank=True, null=True)
    sec_rw_methods = models.PositiveSmallIntegerField(verbose_name="Secondary Reading and Writing Methods (recommended)", blank=True, null=True)

    credits18 = models.CharField(verbose_name="18 credit subjects", blank=True, null=True, max_length=100)
    credits12 = models.CharField(verbose_name="12 credit subjects", blank=True, null=True, max_length = 100)

    em_science = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Science",blank=True, null=True)
    em_math = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Mathematics",blank=True, null=True)
    em_reading = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Reading",blank=True, null=True)
    em_language = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Language Arts",blank=True, null=True)
    em_religion = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Religion",blank=True, null=True)
    em_social = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Social Studies (recommended)",blank=True, null=True)
    em_health = models.PositiveSmallIntegerField(verbose_name="Elementary Methods in Health (recommended)",blank=True, null=True)

    other_ed_credit = models.PositiveSmallIntegerField(verbose_name="Other Professional Education Credits",blank=True, null=True)

    def religion_and_health(self):
        if (self.sop & self.sda_doctrine & self.sda_health & self.sda_history):
            return True
        else:
            return False
    religion_and_health.boolean = True

    def education_credits(self):
        ba_cr = sum(filter(None, [self.sda_education, self.psychology, self.assessment, self.exceptional_child, self.technology]))
        sm_cr = sum(filter(None, [self.sec_methods, self.sec_rw_methods]))
        emr_cr = sum(filter(None, [self.em_science, self.em_math, self.em_reading, self.em_language, self.em_religion]))
        emo_cr = sum(filter(None, [self.em_social, self.em_health]))
        o_cr = sum(filter(None, [self.other_ed_credit]))
        credit = sum(filter(None, [ba_cr, sm_cr, emr_cr, emo_cr, o_cr]))
        return str(credit) + " (20 required)"


    def elementary_methods(self):
         if (self.em_math) and (self.em_science) and (self.em_religion) and (self.em_language) and (self.em_reading):
             return True
         else:
             return False
    elementary_methods.boolean = True


    class Meta:
        ordering = ('teacher',)








