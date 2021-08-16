from django.db import models
from django.contrib.auth.models import User


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
    address = models.CharField(max_length=50, help_text='Enter the address of the school', blank=True, null=True)
    country = models.ForeignKey(Country, on_delete = models.PROTECT)

    ordering = ['name']

    def __str__(self):
        return self.name


# User Model is automatically created by Django and we will extend it to create Teacher Model
# upload will be automatically under the Media_root, which for us is Media
class Teacher(models.Model):
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=False, blank=False)
    suffix = models.CharField(max_length=10, null= True, blank= True)
    active = models.BooleanField (default=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.PROTECT, null=True, help_text="*Required")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='users/ProfilePictures/', default='users/ProfilePictures/blank-profile.jpg', null=True, blank=True)

    class Meta:
        ordering = ('last_name',)

    def name(self):
        if self.middle_name:
            name = self.first_name +" " + self.middle_name+ " "+ self.last_name
        else:
            name = self.first_name + " " + self.last_name
        return name

    def __str__(self):
        return self.first_name + " " + self.last_name

