from django import forms
import django_filters
from django_filters import DateFilter, CharFilter, ChoiceFilter, ModelChoiceFilter

import users.models, teachercert.models
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class CEUInstanceFilter(django_filters.FilterSet):
    teacher = CharFilter(field_name = "ceu_report__teacher", label='Teacher')
    start_date = DateFilter(field_name="date_completed", lookup_expr='gte', label='Completed after:')
    end_date = DateFilter(field_name="date_completed", lookup_expr='lte', label='Completed before:')
    description = CharFilter(field_name='description', lookup_expr='icontains', label='Description')
    school_year = ModelChoiceFilter(field_name='ceu_report__school_year', queryset=SchoolYear.objects.all(), label = 'School_Year')

    CHOICES = (
        ('n', 'Not ISEI Reviewed'),
        ('a', 'ISEI Approved'),
        ('d', 'Not ISEI Approved'),
        ('', 'Any')
    )
    approved = ChoiceFilter(field_name="isei_reviewed", label ='Approved', choices = CHOICES)

class CEUReportFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name="teacher__first_name", label='First Name')
    last_name = CharFilter(field_name="teacher__last_name", label='Last Name')
    school = ModelChoiceFilter(field_name="teacher__user__profile__school__name", label='School', queryset=users.models.School.objects.filter(active=True))
    school_year = ModelChoiceFilter(field_name='school_year', queryset=SchoolYear.objects.all(), label='School Year')
    start_created = DateFilter(field_name="created_at", lookup_expr='gte', label='Created after:',widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    end_created = DateFilter(field_name="created_at", lookup_expr='lte', label='Created before:',widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    start_updated = DateFilter(field_name="updated_at", lookup_expr='gte', label='Updated after:', widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    end_updated = DateFilter(field_name="updated_at", lookup_expr='lte', label='Updated before:', widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))

    CHOICES = (
        ('n', 'Not Reviewed'),
        ('a', 'Approved'),
        ('d', 'Not Approved'),
        ('', 'Any')
    )
    isei_status = ChoiceFilter(field_name="isei_reviewed", choices=CHOICES, label='ISEI approval')
    principal_status = ChoiceFilter(field_name="principal_reviewed", choices=CHOICES, label ='Principal approval')


#not used
class TeacherFilter(django_filters.FilterSet):
    school = CharFilter(field_name = 'school', lookup_expr = 'icontains')

    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user', 'phone', 'profile_picture']


class TCertificateFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name="teacher__first_name", lookup_expr='icontains', label='First Name')
    last_name = CharFilter(field_name="teacher__last_name", lookup_expr='icontains', label='Last Name')
    school = ModelChoiceFilter(field_name="teacher__user__profile__school__name", label='School', queryset=users.models.School.objects.filter(active=True) )
    certificate_type = ModelChoiceFilter(field_name="certification_type", label='Type',
                                         queryset=teachercert.models.CertificationType.objects.all())
    issued_after = DateFilter(field_name="issue_date", lookup_expr='gte', label='Issued after:', widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    issued_before = DateFilter(field_name="issue_date", lookup_expr='lte', label='Issued before:',widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    renew_after = DateFilter(field_name="renewal_date", lookup_expr='gte', label='Renew after:', widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    renew_before = DateFilter(field_name="renewal_date", lookup_expr='lte', label='Renew before:', widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))

    CHOICES = (
        (False, 'Current'),
        (True, 'Archived'),
        (None, 'Any')
    )
    archived = ChoiceFilter(field_name="archived", choices=CHOICES, label='Current/Archived')


class TeacherCertificationApplicationFilter(django_filters.FilterSet):
    school = ModelChoiceFilter(field_name="teacher__user__profile__school__name", label='School', queryset=users.models.School.objects.filter(active=True) )
    first_name = CharFilter(field_name = 'teacher__first_name',label = "First Name", lookup_expr = 'icontains')
    last_name = CharFilter(field_name = 'teacher__last_name',label = "Last Name", lookup_expr = 'icontains')
    CHOICES_B = (
        ('y', 'Billed'),
        ('n', 'Not Billed'),
        ('z', 'N/A'),
    )
    billed = ChoiceFilter(field_name="billed", choices=CHOICES_B, label='Billed')

    CHOICES_C = (
        (False, 'Processing'),
        (True, 'Finalized'),
        (None, 'Any')
    )
    closed = ChoiceFilter(field_name="closed", choices=CHOICES_C, label='Status')
    # CHOICES_D = (
    #     (True, 'Valid'),
    #     (False, 'Expired'),
    #     (None, 'Any')
    # )
    # expired = ChoiceFilter(field_name='expired', choices = CHOICES_D, label = 'Expired')
    applied_after = DateFilter(field_name="date", lookup_expr='gte', label='Applied after:',
                             widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))
    applied_before = DateFilter(field_name="date", lookup_expr='lte', label='Applied before:',
                              widget=DateInput(attrs={'placeholder': 'mm/dd/yyyy'}))


