from django.db import models
#from users.models import *
import os
from django.db import models

from users.models import School, Country, Region, StateField, TNCounty
from teachercert.models import SchoolYear, Teacher
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
import numpy as np

from ISEIapp.storage_backends import MediaStorage


class ReportType(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=3, default="ST")
    order_number = models.PositiveSmallIntegerField(default=0)
    for_all_schools = models.BooleanField(default=False)
    view_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['order_number']

class ReportDueDate(models.Model):
    due_date = models.DateField()
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    opening_report = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Report due dates"
    def __str__(self):
        return self.region.name +", "+ self.report_type.name

    def get_actual_due_date(self, school=None, school_year = None):
        if school:
            try:
                return SchoolSpecificReportDueDate.objects.get(
                    school=school, report_type=self.report_type,
                ).get_actual_due_date(school_year)
            except SchoolSpecificReportDueDate.DoesNotExist:
                pass  # Fallback to the region-based one

        # Fetch the active school year if no school year given
        if not school_year:
            school_year = SchoolYear.objects.get(current_school_year=True)

        # Extract the start and end years from the active school year
        start_year, end_year = map(int, school_year.name.split('-'))

        # Extract the month and day from the due_date field
        month = self.due_date.month
        day = self.due_date.day

        # Use the start year for opening reports, end year otherwise
        if self.opening_report:
            year = start_year
        elif month < 10:
            year = end_year
        else:
            year = start_year

        # Construct a new datetime object with the correct year
        return timezone.datetime(year=year, month=month, day=day).date()

class SchoolSpecificReportDueDate(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    due_date = models.DateField()
    opening_report = models.BooleanField(default=False)

    def get_actual_due_date(self, school_year=None):
        if not school_year:
            school_year = SchoolYear.objects.get(current_school_year=True)

        start_year, end_year = map(int, school_year.name.split('-'))

        month = self.due_date.month
        if self.opening_report and month > 3:
            year = start_year
        else:
            year = end_year

        return timezone.datetime(year=year, month=month, day=self.due_date.day).date()

class AnnualReport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE, null=True, blank=True)
    submit_date = models.DateField(null=True, blank=True)
    last_update_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.report_type.name + " " + self.school.abbreviation + " (" + self.school_year.name + ")"

    class Meta:
        unique_together = (('school', 'school_year', 'report_type'),)
        ordering = ('school_year', 'school', 'report_type')

    def due_date(self):
        # Try to find a school-specific due date first
        specific_due = SchoolSpecificReportDueDate.objects.filter(
            school=self.school, report_type=self.report_type).first()

        if specific_due:
            return specific_due.get_actual_due_date(school_year=self.school_year)

        # Fallback to region-level due date
        region = self.school.street_address.country.region
        region_due = ReportDueDate.objects.filter(
            report_type=self.report_type,region=region).first()

        if region_due:
            return region_due.get_actual_due_date(school=self.school, school_year=self.school_year)

        return None

    def due_date_plus(self,days=None):
        days = days or 14
        return self.due_date() + timezone.timedelta(days=days)


#personnel data collection
    def total_personnel(self):
        return self.personnel_set.exclude(status=StaffStatus.NO_LONGER_EMPLOYED).count()

    def not_returned_personnel(self):
        return self.personnel_set.filter(status=StaffStatus.NO_LONGER_EMPLOYED).count()

    def retention_rate(self):
        total = self.total_personnel()
        if total == 0:
            return None  # or 0.0 if you prefer
        not_returned = self.not_returned_personnel()
        rate = (total - not_returned) / total * 100
        return round(rate, 1)

# Employee Data
class Degree(models.Model):  # Changed to a model
    name = models.CharField(max_length=30, unique=True)
    rank = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class SubjectCategory(models.TextChoices):
    BIBLE = 'B', 'Bible'
    COMPUTER_TECH = 'C', 'Computer/Tech'
    FINE_ARTS = 'F', 'Fine Arts'
    LANGUAGE_ARTS = 'L', 'Language Arts'
    MATH = 'M', 'Math'
    MODERN_LANGUAGE = 'ML', 'Modern Language'
    SCIENCE = 'SC', 'Science'
    SOCIAL_STUDIES = 'SS', 'Social Studies'
    VOCATIONAL_ARTS_COURSES = 'V', 'Vocational Arts Courses'
    WELLNESS_HEALTH_PE = 'W', 'Wellness/Health/PE'
    ELEMENTARY = 'E', 'Elementary'
    MENTORSHIP = 'MT', 'Mentorship'

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=SubjectCategory.choices,
    )

    class Meta:
        ordering = ['category', 'name']
    def __str__(self):
        return self.name

class StaffCategory(models.TextChoices):
    ADMINISTRATIVE = 'A', 'Administrative'
    TEACHING = 'T', 'Teaching'
    GENERAL_STAFF ='G', 'General_Staff'

CATEGORY_EXPLANATION_MAP = {
    'A': '(President, Principal, Vice Principal, Business Manager, Registrar, Vocational Coordinator)',
    'T': '(Teachers, Life Skills Teachers, Deans, Librarian)',
    'G': '(Administrative Asst, Office staff, Vocational supervisors, Food Service Director, School Nurse, Other support staff)',
}

class StaffPosition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=StaffCategory.choices,
    )
    teaching_position=models.BooleanField(default=False)
    class Meta:
        ordering = ['category', 'name']
    def __str__(self):
        return self.name

class StaffStatus(models.TextChoices):
    FULL_TIME = 'FT', 'Full Time'
    PART_TIME = 'PT', 'Part Time'
    VOLUNTEER = 'VO', 'Volunteer'
    NO_LONGER_EMPLOYED = 'NE', 'No Longer Employed'
    LEAVE_OF_ABSENCE = 'LO', 'Leave of Absence'

class Personnel(models.Model):
    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    status = models.CharField("status", max_length=2,
                              choices=StaffStatus.choices, default=StaffStatus.FULL_TIME, )

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    positions = models.ManyToManyField(StaffPosition)
    degrees = models.ManyToManyField(Degree, through='PersonnelDegree', blank=True)

    subjects_teaching = models.ManyToManyField(Subject, blank=True, related_name="subjects_teaching")
    subjects_taught = models.ManyToManyField(Subject, blank=True, related_name="subjects_taught")

    years_work_experience = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Years of Work Experience")
    years_teaching_experience = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Years of Teaching Experience")
    years_administrative_experience = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Years of Administrative Experience")

    years_at_this_school = models.PositiveSmallIntegerField(default=1)

    email_address = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=25, null=True, blank=True)

    sda=models.BooleanField(default=True, verbose_name="SDA")

    class Meta:
        unique_together = (('first_name', 'last_name', 'annual_report'),)

    def __str__(self):
        return self.first_name + " " + self.last_name


class PersonnelDegree(models.Model):  # Now has a foreign key to Degree
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='personnel_degrees')
    area_of_study = models.CharField(max_length=100, null=False, blank=False)


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
        'Graduated':13,
        'GA-I': 14,
        'GA-II': 15,
        'GA-III': 16,
    }
class Student(models.Model):
    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='students', null=False, blank=False, db_index=True)

    name = models.CharField(max_length=200, db_index=True)
    address = models.CharField(max_length=500)
    us_state= StateField(verbose_name="US State", blank=True, null=True)
    TN_county = models.ForeignKey(TNCounty, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, db_index=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unspecified'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')

    birth_date = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    age_at_registration = models.PositiveIntegerField()
    YES_NO_CHOICES = [
        ('Y', 'Yes, SDA'),
        ('O', 'Yes, non-SDA'),
        ('N', 'No'),
        ('U', '-'),
    ]
    boarding = models.BooleanField(default=False)

    baptized = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='U')
    parent_sda = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='U', verbose_name="Parent SDA")

    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('part-time', 'Part Time'),
        ('graduated', 'Graduated'),
        ('did_not_return', 'Did Not Return'),
        ('withdrawn', "Withdrawn"),
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
        (13, 'Graduated'),
        (14, 'GA-I'),
        (15, 'GA-II'),
        (16, 'GA-III'),
    ]
    grade_level =  models.IntegerField(choices=GRADE_LEVEL_CHOICES)

    registration_date = models.DateField(null=True)
    withdraw_date = models.DateField(null=True, blank=True)

    LOCATION_CHOICES = [
        ('on-site', 'On-Site'),
        ('satellite', 'Satellite'),
        ('distance-learning', 'Distance-Learning')

    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='on-site')


    class Meta:
        unique_together = (('name', 'annual_report'),)

    def save(self, *args, **kwargs):
        if self.birth_date and self.registration_date:
            self.age_at_registration = self.registration_date.year - self.birth_date.year - (
                    (self.registration_date.month, self.registration_date.day) < (
                self.birth_date.month, self.birth_date.day))
        elif self.age:
            self.age_at_registration = self.age
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + "," + self.annual_report.school_year.name


class Day190(models.Model):
    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE, related_name='day190', null=False, blank=False)
    start_date = models.DateField(verbose_name= "School-year start date", default=None, null=True, blank=True)
    end_date = models.DateField(verbose_name= "School-year end date", default=None, null=True, blank=True)
    number_of_days = models.PositiveIntegerField(verbose_name= "Number of School Days", default=0)
    inservice_days = models.PositiveIntegerField(verbose_name="In-service and Discretionary Days", default=0)
    file = models.FileField(upload_to='School_calendars/%Y', storage=MediaStorage(), null=True, blank=True, verbose_name="School Calendar/%Y")
    calendar_link = models.URLField(null=True, blank=True, verbose_name="School Calendar Link")
    comment = models.TextField(verbose_name="Comment", null=True, blank=True)

    def __str__(self):
        return str(self.annual_report)


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
        ('IS', 'ISEI Workshop'),
        ('TE', 'Teacher/Administrator Evaluation'),
        ('TC', 'Teacher Convention'),
        ('OT', 'Other'),
        ('DS', 'Discretionary'),
    ]

    day190 = models.ForeignKey(Day190, related_name='inservice_discretionary_days', on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    dates = models.CharField(max_length=20)
    hours = models.PositiveIntegerField()


class AbbreviatedDays(models.Model):
    day190 = models.ForeignKey(Day190, related_name='abbreviated_days', on_delete=models.CASCADE)
    date = models.CharField(max_length=255)
    hours = models.PositiveIntegerField()

class SundaySchoolDays(models.Model):
    day190 = models.ForeignKey(Day190, related_name='sunday_school_days', on_delete=models.CASCADE)
    date = models.DateField()
    TYPE_CHOICES = [
        (None, '--------------'),
        ('RC', 'Regular Classes'),
        ('FT', 'Field Trip'),
        #('MT', 'Mission Trip'),
        #('SL', 'Service Learning'),
        #('MU', 'Music Trip'),
        ('OT', 'Other Education Enrichment Activity'),
        ('ST', 'Standardized Testing'),
        ('GR', 'Graduation'),
    ]
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)


class EducationalEnrichmentActivity(models.Model):
    day190 = models.ForeignKey(Day190, related_name='educational_enrichment_activities', on_delete=models.CASCADE)
    TYPE_CHOICES = [
        (None, '--------------'),
        ('FT', 'Field Trip'),
        ('MT', 'Mission Trip'),
        ('SL', 'Service Learning'),
        ('MU', 'Music Trip'),
        ('OT', 'Other Education Enrichment Activity'),
    ]
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    dates = models.CharField(max_length=255)
    days = models.PositiveIntegerField()

    class Meta:
        unique_together = (('day190', 'dates', 'type'),)


class Inservice(models.Model):
    dates = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    presenter = models.CharField(max_length=255)
    hours = models.PositiveIntegerField()
    annual_report = models.ForeignKey(AnnualReport, on_delete=models.CASCADE)

    def __str__(self):
        return self.topic


class GradeCount(models.Model):
    pre_k_count = models.PositiveSmallIntegerField(default=0, verbose_name="Pre-K")
    k_count = models.PositiveSmallIntegerField(default=0, verbose_name="K")
    grade_0_count = models.PositiveSmallIntegerField(default=0, verbose_name="0")
    grade_1_count = models.PositiveSmallIntegerField(default=0, verbose_name="1")
    grade_2_count = models.PositiveSmallIntegerField(default=0, verbose_name="2")
    grade_3_count = models.PositiveSmallIntegerField(default=0, verbose_name="3")
    grade_4_count = models.PositiveSmallIntegerField(default=0, verbose_name="4")
    grade_5_count = models.PositiveSmallIntegerField(default=0, verbose_name="5")
    grade_6_count = models.PositiveSmallIntegerField(default=0, verbose_name="6")
    grade_7_count = models.PositiveSmallIntegerField(default=0, verbose_name="7")
    grade_8_count = models.PositiveSmallIntegerField(default=0, verbose_name="8")
    grade_9_count = models.PositiveSmallIntegerField(default=0, verbose_name="9")
    grade_10_count = models.PositiveSmallIntegerField(default=0, verbose_name="10")
    grade_11_count = models.PositiveSmallIntegerField(default=0, verbose_name="11")
    grade_12_count = models.PositiveSmallIntegerField(default=0, verbose_name="12")
    ga_i_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-I")
    ga_ii_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-II")
    ga_iii_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-III")

    def total_count(self):
        return (
                self.pre_k_count + self.k_count + self.grade_0_count + self.grade_1_count +
                self.grade_2_count + self.grade_3_count + self.grade_4_count +
                self.grade_5_count + self.grade_6_count + self.grade_7_count +
                self.grade_8_count + self.grade_9_count + self.grade_10_count +
                self.grade_11_count + self.grade_12_count +
                self.ga_i_count + self.ga_ii_count + self.ga_iii_count
        )

    def academy_count(self):
        return (self.grade_9_count + self.grade_10_count +
                self.grade_11_count + self.grade_12_count)


class PartTimeGradeCount(models.Model):
    pre_k_count = models.PositiveSmallIntegerField(default=0, verbose_name="Pre-K")
    k_count = models.PositiveSmallIntegerField(default=0, verbose_name="K")
    grade_0_count = models.PositiveSmallIntegerField(default=0, verbose_name="0")
    grade_1_count = models.PositiveSmallIntegerField(default=0, verbose_name="1")
    grade_2_count = models.PositiveSmallIntegerField(default=0, verbose_name="2")
    grade_3_count = models.PositiveSmallIntegerField(default=0, verbose_name="3")
    grade_4_count = models.PositiveSmallIntegerField(default=0, verbose_name="4")
    grade_5_count = models.PositiveSmallIntegerField(default=0, verbose_name="5")
    grade_6_count = models.PositiveSmallIntegerField(default=0, verbose_name="6")
    grade_7_count = models.PositiveSmallIntegerField(default=0, verbose_name="7")
    grade_8_count = models.PositiveSmallIntegerField(default=0, verbose_name="8")
    grade_9_count = models.PositiveSmallIntegerField(default=0, verbose_name="9")
    grade_10_count = models.PositiveSmallIntegerField(default=0, verbose_name="10")
    grade_11_count = models.PositiveSmallIntegerField(default=0, verbose_name="11")
    grade_12_count = models.PositiveSmallIntegerField(default=0, verbose_name="12")
    ga_i_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-I")
    ga_ii_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-II")
    ga_iii_count = models.PositiveSmallIntegerField(default=0, verbose_name="GA-III")

    def total_count(self):
        return (
                self.pre_k_count + self.k_count + self.grade_1_count +
                self.grade_2_count + self.grade_3_count + self.grade_4_count +
                self.grade_5_count + self.grade_6_count + self.grade_7_count +
                self.grade_8_count + self.grade_9_count + self.grade_10_count +
                self.grade_11_count + self.grade_12_count +
                self.ga_i_count + self.ga_ii_count +self.ga_iii_count
        )

class Opening(models.Model):
    annual_report = models.OneToOneField(AnnualReport, on_delete=models.CASCADE, related_name='opening', null=False, blank=False)
    grade_count=models.OneToOneField(GradeCount, on_delete=models.CASCADE, related_name='opening', null=True, blank=True)
    part_time_grade_count=models.OneToOneField(PartTimeGradeCount, on_delete=models.CASCADE, related_name='opening', null=True, blank=True)

    graduated_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Graduated")
    did_not_return_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Did Not Return")

    girl_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Girls")
    boy_count=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boys")
#boarding/day student count
    boarding_girl_count_E = models.PositiveSmallIntegerField(null=True, blank=True,verbose_name="Boarding Girls E")
    boarding_boy_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boarding Boys E")
    boarding_girl_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boarding Girls S")
    boarding_boy_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boarding Boys S")

    day_girl_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Girls E")
    day_boy_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Boys E")
    day_girl_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Girls S")
    day_boy_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Boys S")

    boarding_boy_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boarding Boys GA")
    boarding_girl_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Boarding Girls GA")
    day_boy_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Boys GA")
    day_girl_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Day Girl GA")


#baptismal status
    baptized_parent_sda_count_K = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name= "Baptised with at least one parents SDA K")
    baptized_parent_non_sda_count_K = models.PositiveSmallIntegerField(null=True, blank=True,  verbose_name= "Baptised with non-SDA parents K")
    unbaptized_parent_sda_count_K = models.PositiveSmallIntegerField(null=True, blank=True,  verbose_name= "Not baptised with at least one parents SDA K")
    unbaptized_parent_non_sda_count_K = models.PositiveSmallIntegerField(null=True, blank=True,  verbose_name= "Not baptised with non-SDA parents K")

    baptized_parent_sda_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with at least one parents SDA")
    baptized_parent_non_sda_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with non-SDA parents")
    unbaptized_parent_sda_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with at least one parents SDA")
    unbaptized_parent_non_sda_count_E = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with non-SDA parents")

    baptized_parent_sda_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with at least one parents SDA S")
    baptized_parent_non_sda_count_S = models.PositiveSmallIntegerField(null=True, blank=True,verbose_name="Baptised with non-SDA parents S")
    unbaptized_parent_sda_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with at least one parents SDA S")
    unbaptized_parent_non_sda_count_S = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with non-SDA parents S")

    baptized_parent_sda_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with at least one parents SDA GA")
    baptized_parent_non_sda_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with non-SDA parents GA")
    unbaptized_parent_sda_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with at least one parents SDA GA")
    unbaptized_parent_non_sda_count_GA = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not baptised with non-SDA parents GA")

    unknown_baptismal_statut_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Unknown baptismal status")
    baptized_non_sda_count=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Baptised with non-SDA count")

    #staff count
    teacher_admin_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Administrative and Teaching Staff")
    general_staff_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="General Staff")

    non_sda_teacher_admin_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="non-SDA Administrative and Teaching Staff")

    associate_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Associate")
    bachelor_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Bachelor")
    masters_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Masters")
    doctorate_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Doctorate")
    professional_count = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Professional")

    @property
    def opening_enrollment(self):
        if self.grade_count:
            return self.grade_count.total_count()
        else:
            return None

    @property
    def retention_percentage(self):
        total = self.opening_enrollment
        if total == 0:
            return None  # or 0.0 or "N/A", depending on how you want to handle divide-by-zero
        leavers = (self.did_not_return_count or 0)
        retained = total - leavers
        return round((retained / total) * 100, 1)

    @property
    def girl_percentage(self):
        if self.opening_enrollment and self.girl_count:
            total = self.opening_enrollment
            if total == 0:
                return None
            return round((self.girl_count or 0) / total * 100, 1)
        else:
            return None

    @property
    def boy_percentage(self):
        if self.opening_enrollment and self.boy_count:
            total = self.opening_enrollment
            if total == 0:
                return None
            return round((self.boy_count or 0) / total * 100, 1)
        else:
            return None

    def __str__(self):
        return str(self.annual_report)


class Closing(models.Model):
    annual_report = models.OneToOneField(AnnualReport, on_delete=models.CASCADE, related_name='closing')

    grade_count = models.OneToOneField(GradeCount, on_delete=models.CASCADE, related_name='closing', null=True, blank=True)
    part_time_grade_count = models.OneToOneField(PartTimeGradeCount, on_delete=models.CASCADE, related_name='closing', null=True, blank=True)
    withdraw_count=models.PositiveSmallIntegerField(null=True, blank=True)
    new_student_count=models.PositiveSmallIntegerField(null=True, blank=True)

    final_school_day=models.DateField(null=True, blank=True, verbose_name="Final date school was in full session (last academic school day)")

    no_mission_trips = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Not organized by the school")
    no_mission_trips_school=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Planned or executed by your school")
    mission_trip_locations=models.CharField(max_length=255, null=True, blank=True, verbose_name="Location of Mission trips")
    student_lead_evangelistic_meetings=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Number of Student Lead Evangelistic Meetings")
    evangelistic_meeting_locations=models.CharField(max_length=255, null=True, blank=True, verbose_name="Location of Evangelistic Meetings")

    student_evangelistic_meetings_baptism= models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Total number of baptisms as a result of student evangelism")
    student_baptism_sda_parent = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Student Baptised during the past 12 months (SDA parent(s))")
    student_baptism_non_sda_parent = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Student Baptised with non-SDA parent(s)")

    outreach = models.TextField(null=True, blank=True, verbose_name="Other Outreach Activities")

    def __str__(self):
        return str(self.annual_report)

    @property
    def baptized_students(self):
        return (self.student_baptism_sda_parent or 0) + (self.student_baptism_non_sda_parent or 0)

    @property
    def withdrawn_percentage(self):
        if not self.grade_count or self.grade_count.total_count() == 0:
            return None
        return round((self.withdraw_count or 0) / (self.grade_count.total_count()+(self.withdraw_count or 0)) * 100, 1)


class WorthyStudentScholarship(models.Model):
    annual_report = models.OneToOneField(AnnualReport, on_delete=models.CASCADE, related_name='worthy_student')

    opening_enrollment = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Opening Enrollment (9-12th grade)")
    closing_enrollment = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Closing Enrollment (9-12th grade)")

    school_generated_fund=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Academy Generated Worthy Student Fund distributed")
    wss_fund = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Worthy Student Scholarship Fund money distributed")

    students_assisted_total=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Number of students assisted from ALL funds")
    students_assisted_wss= models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Number of students assisted from Worthy Student Scholarship Fund")

    next_year_budget=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Amount of academy generated worthy student money budgeted for next year")

    letter = models.FileField(upload_to='wss_letters/%Y', storage=MediaStorage(), null=True, blank=True, verbose_name="Thank you letter")
    def __str__(self):
        return str(self.annual_report)

    def get_verbose_field_name(self, field_name):
        return str(self._meta.get_field(field_name).verbose_name)


class LongitudinalEnrollment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="enrollment_records")
    year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="enrollment_records")
    grade = models.IntegerField(choices=[(key, value) for key, value in GRADE_LEVEL_DICT.items()])
    enrollment_count = models.PositiveIntegerField(default=0)  # Total students in this grade/year

    class Meta:
        unique_together = ("school", "year", "grade")  # Ensure unique records for each grade-year
    def __str__(self):
        return f"{self.school.name} - Grade {self.grade} ({self.year}) - Enrollment {self.enrollment_count}"