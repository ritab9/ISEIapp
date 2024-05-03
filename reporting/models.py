from django.db import models
from users.models import *
import os

from django.db import models
from users.models import School, Country
from teachercert.models import SchoolYear

class Student(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)  # This field is not necessarily required at model level.
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    birth_date = models.DateField()
    grade_level = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    baptized = models.BooleanField(null=True)
    is_at_least_one_parent_sda = models.BooleanField(null=True)

    def __str__(self):
        return self.name

class StudentReport(models.Model):
    LOCATION_CHOICES = [
        ('on-site', 'On-Site'),
        ('satelite', 'Satelite'),
        ('distance-learning', 'Distance-Learning')
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    registration_date = models.DateField()
    withdraw_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='on-site')

    age_at_registration = models.PositiveIntegerField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.student.birthday and not self.age_at_registration:
            today = date.today()
            self.age_at_registration = today.year - self.student.birthday.year - (
                        (today.month, today.day) < (self.student.birthday.month, self.student.birthday.day))
        super().save(*args, **kwargs)



class AnnualReport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    student_report = models.OneToOneField(StudentReport, on_delete=models.CASCADE)