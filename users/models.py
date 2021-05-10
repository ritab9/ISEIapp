from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class School(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the name of the school', unique=True, blank=False,
                            null=False)
    address = models.CharField(max_length=50, help_text='Enter the name of the school', blank=True, null=True)
    abbreviation = models.CharField(max_length=4, default=" ", help_text=' Enter the abbreviation for this school')
    ordering = ['name']

    def __str__(self):
        return self.name


# User Model is automatically created by Django and we will extend it to create Teacher Model
#upload will be automatically under the Media_root, which for us is Media
class Teacher(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.PROTECT, null=True, help_text="*Required")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='users/ProfilePictures/', default='users/ProfilePictures/blank-profile.jpg', null=True, blank=True)
    CERTIFICATION_TYPES = {
        ('v', 'Vocational'),
        ('d', 'Designated'),
        ('c', 'Conditional'),
        ('e', 'Semi Professional'),
        ('b', 'Basic'),
        ('s', 'Standard'),
        ('p', 'Professional'),
        ('n', 'None')
    }
    current_certification = models.CharField(max_length=1, choices=sorted(CERTIFICATION_TYPES), null=True, blank=True)

    def __str__(self):
        return self.user.last_name + ', ' + self.user.first_name

