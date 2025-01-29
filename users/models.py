from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from django.apps import apps


class TNCounty(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class StateField(models.CharField):
    STATE_CHOICES = [
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    ]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['choices'] = self.STATE_CHOICES
        super().__init__(*args, **kwargs)


class Region(models.Model):
    name = models.CharField(max_length=25, unique = True)
    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique = True)
    code = models.CharField(max_length=3, unique = True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    ordering = ['name']
    student_occurrence = models.PositiveIntegerField(default=0)
    student_occurrence_log = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-student_occurrence_log', 'name']


class School(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the name of the school', unique=True, blank=False,
                            null=False)
    abbreviation = models.CharField(max_length=6, default=" ", help_text=' Enter the abbreviation for this school')
    ordering = ['name']
    foundation = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    principal = models.CharField(max_length=100, blank=True, null=True)
    president = models.CharField(max_length=100, blank=True, null=True)
    member = models.BooleanField(default=True)
    textapp= models.CharField(max_length=20, blank=True, null=True)
    fire_marshal_date = models.DateField(blank=True, null=True, verbose_name='Date of Last Fire Marshal Inspection')
    active=models.BooleanField(default=True)
    test=models.BooleanField(default=False)
    initial_accreditation_date= models.DateField(blank=True, null=True)
    worthy_student_report_needed = models.BooleanField(default=False)

    TYPE_CHOICES = [
        ('K-8', 'K-8'),
        ('K-12', 'K-12'),
        ('9-12', '9-12'),
    ]
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default='9-12',
                                   verbose_name="Type of School")

    current_school_year=models.ForeignKey('teachercert.SchoolYear', on_delete=models.CASCADE, null=True, blank=True)

    def current_accreditation(self):
        Accreditation = apps.get_model('accreditation', 'Accreditation')  # Lazy load the Accreditation model
        return Accreditation.objects.filter(school=self, status='current').first()

    def get_active_users(school):
        return User.objects.filter(profile__school=school, is_active=True).distinct()

    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.address:
            raise ValidationError("Address is required for this school.")
        super(School, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class AccreditationAgency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10)
    def __str__(self):
        return self.abbreviation

class OtherAgencyAccreditationInfo(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    agency = models.ForeignKey(AccreditationAgency, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    current_accreditation = models.BooleanField(default=False)
    class Meta:
        unique_together = ['school', 'agency', 'current_accreditation']
    def __str__(self):
        return self.school.name+','+self.agency.abbreviation


# User Model is automatically created by Django and we will extend it to create other models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    school = models.ForeignKey(School, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return str(self.user) + ", " + self.school.name

#Teacher Models
class Teacher(models.Model):

    joined_at = models.DateField(auto_now_add=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20)
    suffix = models.CharField(max_length=10, null= True, blank= True)
    date_of_birth = models.DateField(null= True)
    school = models.ForeignKey(School, on_delete=models.PROTECT, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='users/ProfilePictures/', default='users/ProfilePictures/blank-profile.jpg', null=True, blank=True)
    sda = models.BooleanField(default=True)
    home_church = models.CharField(max_length=30, null=True, blank=True)
    #academic = models.BooleanField(default=True)
    background_check=models.BooleanField(default=False)

    class Meta:
        ordering = ('last_name',)

    def name(self):
        if self.middle_name and self.suffix:
            name = self.last_name + ", " + self.first_name + " " + self.middle_name + " " + self.suffix
        else:
            if self.middle_name:
                name = self.last_name + ", " + self.first_name + " " + self.middle_name
            elif self.suffix:
                name = self.last_name + ", " + self.first_name + " " + self.suffix
            else:
                name = self.last_name + ", " + self.first_name
        return name

    def iseiteacherid(self):
        l = len(str(self.user.id))
        if l==1:
            teacher_id = "000" + str(self.user.id)
        elif l==2:
            teacher_id = "00"+str(self.user.id)
        elif l==3:
            teacher_id = "0" + str(self.user.id)
        else:
            teacher_id = str(self.user.id)

        return str(self.joined_at.year) + "-" + teacher_id

    def __str__(self):
        return self.last_name + ", " + self.first_name

class College(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False,
                            null=False)
    address = models.CharField(verbose_name="City, State, Country", max_length=40, default="",)
    ordering = ['name']

    def __str__(self):
        return self.name

class CollegeAttended(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=60, verbose_name="College Name", null=False, blank=False,)
    address = models.CharField(verbose_name="City, Country", max_length=40, default="", )
    start_date = models.CharField(verbose_name = "Start Year", max_length= 4, null=False, blank=False, help_text="yyyy")
    end_date = models.CharField(verbose_name = "End Year", max_length=4, null=False, blank=False, help_text="yyyy")
    LEVELS = (
        ('a', 'Associate degree'),
        ('b', "Bachelor's degree"),
        ('m', "Master's degree"),
        ('d', 'Doctoral degree'),
        ('c', 'Certificate'),
        ('n', 'None')
    )
    level = models.CharField(max_length=1, choices=LEVELS, help_text="Degree Level", null=False, blank=False)
    degree = models.CharField(max_length=40, verbose_name= "Type, Degree Earned", help_text= "BSc, Marketing & Psychology", null= True, blank=True)
    transcript_requested = models.BooleanField(default= False, verbose_name="Transcripts requested")
    transcript_received = models.BooleanField(default= False, null = False, blank= False, verbose_name="Received")
    transcript_processed = models.BooleanField(default=False, null=False, blank= False, verbose_name = "Processed")
    def __str__(self):
        return self.name

    class Meta:
        ordering = ('transcript_processed', 'transcript_received', 'transcript_requested','teacher','-end_date',)

class SchoolOfEmployment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=50, unique=False, blank=False, null=False)
    address = models.CharField(verbose_name="City, Country", max_length=40, default="", )
    start_date = models.CharField(max_length=10, null=False, blank=False, help_text="mm/yyyy or yyyy")
    end_date = models.CharField(max_length=10, null=False, blank=False, help_text="mm/yyyy or yyyy or 'to date'")
    courses = models.CharField(verbose_name="Courses taught", max_length=100, default="", )

    class Meta:
        ordering = ('-end_date',)

    def __str__(self):
        return self.name

#Other user Models

class Address(models.Model):
    address_1 = models.CharField(verbose_name="address", max_length=128)
    address_2 = models.CharField(verbose_name="address cont'd", max_length=128, blank=True)
    city= models.CharField(verbose_name="city", max_length=64, default="")
    state_us = StateField(verbose_name="US State", blank=True, null=True)
    tn_county = models.ForeignKey(TNCounty, on_delete=models.SET_NULL, null=True, blank=True)
    zip_code = models.CharField(verbose_name="zip/postal code", max_length=8, default="")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    school = models.OneToOneField(School, on_delete=models.CASCADE, blank=True, null=True)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.city + "," + self.country.name

