from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USSocialSecurityNumberField
from datetime import date



# Create your models here.

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

    def __str__(self):
        return self.name


# User Model is automatically created by Django and we will extend it to create Teacher Model
# upload will be automatically under the Media_root, which for us is Media
class Teacher(models.Model):
    #TODO once all data is entered make joined_at auto field
    #joined_at = models.DateField(auto_now_add=True, blank=True)
    joined_at = models.DateField()

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20)
    suffix = models.CharField(max_length=10, null= True, blank= True)
    date_of_birth = models.DateField(null= True)
    active = models.BooleanField (default=True)
    school = models.ForeignKey(School, on_delete=models.PROTECT, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='users/ProfilePictures/', default='users/ProfilePictures/blank-profile.jpg', null=True, blank=True)


    class Meta:
        ordering = ('school','last_name',)

    def name(self):
        if self.middle_name and self.suffix:
            name = self.first_name +" " + self.middle_name+ " "+ self.last_name + " " +self.suffix
        else:
            if self.middle_name:
                name = self.first_name + " " + self.middle_name + " " + self.last_name
            elif self.suffix:
                name = self.first_name + " " + self.last_name + "" + self.suffix
            else:
                name = self.first_name + " " + self.last_name
        return name

    def iseiteacherid(self):
        l = len(str(self.id))
        if l==1:
            teacher_id = "000" + str(self.id)
        elif l==2:
            teacher_id = "00"+str(self.id)
        elif l==3:
            teacher_id = "0" + str(self.id)
        else:
            teacher_id = str(self.id)

        return str(self.joined_at.year) + "-" + teacher_id

    def __str__(self):
        return self.first_name + " " + self.last_name


class Address(models.Model):
    address_1 = models.CharField(verbose_name="address", max_length=128)
    address_2 = models.CharField(verbose_name="address cont'd", max_length=128, blank=True)
    city = models.CharField(verbose_name="city", max_length=64, default="")
    state = models.CharField(verbose_name="state or province", max_length=4, default="")
    zip_code = models.CharField(verbose_name="zip/postal code", max_length=8, default="")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    school = models.OneToOneField(School, on_delete=models.CASCADE, blank=True, null=True)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.city +"," +self.country.name


class College(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False,
                            null=False)
    address = models.CharField(verbose_name="City, State, Country", max_length=40, default="",)
    ordering = ['name']

    def __str__(self):
        return self.name

class CollegeAttended(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=30, verbose_name="College Name", null=False, blank=False,)
    address = models.CharField(verbose_name="City, Country", max_length=40, default="", )
    start_date = models.DateField(null=False, blank=False, help_text="mm/dd/yyyy")
    end_date = models.DateField(null=False, blank=False, help_text="mm/dd/yyyy")
    LEVELS = (
        ('a', 'Associate degree'),
        ('b', "Bachelor's degree"),
        ('m', "Master's degree"),
        ('d', 'Doctoral degree'),
    )
    level = models.CharField(max_length=1, choices=LEVELS, help_text="Degree Level", null=False, blank=False)
    degree = models.CharField(max_length=40, verbose_name= "Type, Degree Earned", help_text= "BSc, Marketing & Psychology", null= False, blank=False)
    transcript_requested = models.BooleanField(default= False, verbose_name="Official college transcripts have been requested")
    transcript_received = models.BooleanField(default= False, null = False, blank= False)
    transcript_processed = models.BooleanField(default=False, null=False, blank= False)
    def __str__(self):
        return self.name

class SchoolOfEmployment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    address = models.CharField(verbose_name="City, Country", max_length=40, default="", )
    start_date = models.DateField(null=False, blank=False, help_text="mm/dd/yyyy")
    end_date = models.DateField(null=False, blank=False, help_text="mm/dd/yyyy")
    courses = models.CharField(verbose_name="Courses taught", max_length=100, default="", )
    def __str__(self):
        return self.name
