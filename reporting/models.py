from django.db import models
#from users.models import *
import os

from users.models import School, Country, Region, StateField, TNCounty
from teachercert.models import SchoolYear
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms


class ReportType(models.Model):
    name = models.CharField(max_length=255)
    order_number = models.PositiveSmallIntegerField(default=0)
    def __str__(self):
        return self.name

class ReportDueDate(models.Model):
    due_date = models.DateField()
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    opening_report = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Report due dates"
    def __str__(self):
        return self.region.name +", "+ self.report_type.name
    def get_actual_due_date(self):
        # Fetch the active school year
        current_year = SchoolYear.objects.get(current_school_year=True)

        # Extract the start and end years from the active school year
        start_year, end_year = map(int, current_year.name.split('-'))

        # Extract the month and day from the due_date field
        month = self.due_date.month
        day = self.due_date.day

        # Use the start year for opening reports, end year otherwise
        year = start_year if self.opening_report else end_year

        # Construct a new datetime object with the correct year
        return timezone.datetime(year=year, month=month, day=day).date()


class AnnualReport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE, null=True, blank=True)
    unique_together = (('school', 'school_year', report_type),)
    submit_date = models.DateField(null=True, blank=True)
    last_update_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.school.name + "," + self.school_year.name + ","+self.report_type.name


GRADE_LEVEL_DICT = {
        'Pre-K': -2,
        'K': -1,
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        '11': 11,
        '12': 12,
    }
class Student(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    us_state= StateField(verbose_name="US State", blank=True, null=True)
    TN_county = models.ForeignKey(TNCounty, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    age_at_registration = models.PositiveIntegerField()
    STATUS_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
        ('U', 'Unknown'),
    ]

    baptized = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U')
    parent_sda = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U', verbose_name="Parent SDA")

    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('graduated', 'Graduated Last Year'),
        ('did_not_return', 'Did Not Return'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='enrolled')

    GRADE_LEVEL_CHOICES = [
        (-2, 'Pre-K'),
        (-1, 'K'),
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
    ]
    grade_level =  models.IntegerField(choices=GRADE_LEVEL_CHOICES)

    registration_date = models.DateField()
    withdraw_date = models.DateField(null=True, blank=True)

    LOCATION_CHOICES = [
        ('on-site', 'On-Site'),
        ('satelite', 'Satelite'),
        ('distance-learning', 'Distance-Learning')

    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='on-site')

    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='students', null=False, blank=False)

    unique_together = (('name', 'birth_date', 'annual_report'),)

    def save(self, *args, **kwargs):
        if self.birth_date and self.registration_date and not self.age_at_registration:
            self.age_at_registration = self.registration_date.year - self.birth_date.year - (
                    (self.registration_date.month, self.registration_date.day) < (
                self.birth_date.month, self.birth_date.day))
        elif self.age and not self.age_at_registration:
            self.age_at_registration = self.age
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + "," + self.annual_report.school_year.name
