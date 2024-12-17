import django_filters
from django_filters import DateFilter, CharFilter, ChoiceFilter, BooleanFilter, ModelChoiceFilter
from django.contrib.auth.models import Group


from .models import *


class SchoolFilter(django_filters.FilterSet):
    school = ModelChoiceFilter(field_name="school__name", label='School', queryset=School.objects.filter(active=True) )

