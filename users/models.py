from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USSocialSecurityNumberField
from datetime import date



class StateField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['choices'] = [
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
        super().__init__(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=25, unique = True)
    code = models.CharField(max_length=3, unique = True)
    REGIONS = {
        ('a', 'Asia'),
        ('e', 'Europe'),
        ('n', 'North America'),
    }
    region = models.CharField(max_length=1, choices=sorted(REGIONS), null=False, blank=False)

    def __str__(self):
        return self.code


class School(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the name of the school', unique=True, blank=False,
                            null=False)
    abbreviation = models.CharField(max_length=4, default=" ", help_text=' Enter the abbreviation for this school')
    ordering = ['name']
    foundation = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


# User Model is automatically created by Django and we will extend it to create Teacher Model
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
    state_old = models.CharField(verbose_name="state or province", max_length=4, default="")
    state = StateField(blank=True, null=True)
    zip_code = models.CharField(verbose_name="zip/postal code", max_length=8, default="")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    school = models.OneToOneField(School, on_delete=models.CASCADE, blank=True, null=True)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.city + "," + self.country.name
