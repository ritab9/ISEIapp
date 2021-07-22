
import django_filters
from django_filters import DateFilter, CharFilter, ChoiceFilter, BooleanFilter, ModelChoiceFilter

import users.models
from .models import *


class PDAInstanceFilter(django_filters.FilterSet):
    teacher = CharFilter(field_name = "pda_report__teacher", label='Teacher')
    start_date = DateFilter(field_name="date_completed", lookup_expr='gte', label='Completed after:')
    end_date = DateFilter(field_name="date_completed", lookup_expr='lte', label='Completed before:')
    description = CharFilter(field_name='description', lookup_expr='icontains', label='Description')
    school_year = ModelChoiceFilter(field_name='pda_report__school_year', queryset=SchoolYear.objects.all(), label = 'School_Year')

    CHOICES = (
        ('n', 'Not ISEI Reviewed'),
        ('a', 'ISEI Approved'),
        ('d', 'Not ISEI Approved'),
        ('', 'Any')
    )
    approved = ChoiceFilter(field_name="isei_reviewed", label ='Approved', choices = CHOICES)

class PDAReportFilter(django_filters.FilterSet):
    first_name = CharFilter(field_name="teacher__first_name", label='First Name')
    last_name = CharFilter(field_name="teacher__last_name", label='Last Name')
    school = ModelChoiceFilter(field_name="teacher__school__name", label='School', queryset=users.models.School.objects.all() )
    school_year = ModelChoiceFilter(field_name='school_year', queryset=SchoolYear.objects.all(), label='School Year')
    start_created = DateFilter(field_name="created_at", lookup_expr='gte', label='Created after:')
    end_created = DateFilter(field_name="created_at", lookup_expr='lte', label='Created before:')
    start_updated = DateFilter(field_name="updated_at", lookup_expr='gte', label='Updated after:')
    end_updated = DateFilter(field_name="updated_at", lookup_expr='lte', label='Updated before:')

    CHOICES = (
        ('n', 'Not Reviewed'),
        ('a', 'Approved'),
        ('d', 'Not Approved'),
        ('', 'Any')
    )
    isei_status = ChoiceFilter(field_name="isei_reviewed", choices=CHOICES, label='ISEI approval')
    principal_status = ChoiceFilter(field_name="principal_reviewed", choices=CHOICES, label ='Principal approval')





class TeacherFilter(django_filters.FilterSet):
    school = CharFilter(field_name = 'school', lookup_expr = 'icontains')
    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user', 'phone', 'profile_picture']
