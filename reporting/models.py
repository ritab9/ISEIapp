from django.db import models
#from users.models import *
import os

from users.models import School, Country, Region, StateField, TNCounty
from teachercert.models import SchoolYear
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
import numpy as np


class ReportType(models.Model):
    name = models.CharField(max_length=255)
    order_number = models.PositiveSmallIntegerField(default=0)
    for_all_schools = models.BooleanField(default=False)
    isei_created = models.BooleanField(default=False)
    view_name = models.CharField(max_length=255, null=True, blank=True)

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
    submit_date = models.DateField(null=True, blank=True)
    last_update_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.school.name + ", " + self.school_year.name + ", "+self.report_type.name

    class Meta:
        unique_together = (('school', 'school_year', 'report_type'),)

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
    name = models.CharField(max_length=200, db_index=True)
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
        ('U', '-'),
    ]
    boarding = models.BooleanField(default=False)

    baptized = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U')
    parent_sda = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U', verbose_name="Parent SDA")

    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('graduated', 'Graduated'),
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
        (13, 'Graduated')
    ]
    grade_level =  models.IntegerField(choices=GRADE_LEVEL_CHOICES)

    registration_date = models.DateField()
    withdraw_date = models.DateField(null=True, blank=True)

    LOCATION_CHOICES = [
        ('on-site', 'On-Site'),
        ('satellite', 'Satellite'),
        ('distance-learning', 'Distance-Learning')

    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='on-site')

    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='students', null=False, blank=False)

    class Meta:
        unique_together = (('name', 'annual_report'),)

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


class Day190(models.Model):
    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='day190', null=False, blank=False)
    start_date = models.DateField(verbose_name= "School-year start date", default=None, null=True, blank=True)
    end_date = models.DateField(verbose_name= "School-year end date", default=None, null=True, blank=True)
    number_of_sundays = models.PositiveIntegerField(verbose_name="Number of Sunday school days", default=0)
    number_of_days = models.PositiveIntegerField(verbose_name= "Number of School Days", default=0)
    inservice_days = models.PositiveIntegerField(verbose_name="In-service and Discretionary Days", default=0)



class Vacations(models.Model):
    day190 = models.ForeignKey(Day190, related_name='vacations', on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    start_date = models.DateField()
    end_date = models.DateField()
    weekdays = models.IntegerField()


class InserviceDiscretionaryDays(models.Model):
    TYPE_CHOICES = [
        ('CI', 'Curriculum Improvement'),
        ('II', 'Instructional Improvement'),
        ('CM', 'Classroom Management'),
        ('TE', 'Teacher/Administrator Evaluation'),
        ('TC', 'Teacher Convention'),
        ('OT', 'Other'),
        ('DS', 'Discretionary'),
    ]

    day190 = models.ForeignKey(Day190, related_name='inservice_discretionary_days', on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='CI')
    dates = models.CharField(max_length=255)
    hours = models.PositiveIntegerField()


class AbbreviatedDays(models.Model):
    day190 = models.ForeignKey(Day190, related_name='abbreviated_days', on_delete=models.CASCADE)
    date = models.CharField(max_length=255)
    hours = models.PositiveIntegerField()