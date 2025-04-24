import django_filters
from django_filters import DateFilter, CharFilter, ChoiceFilter, BooleanFilter, ModelChoiceFilter
from django.contrib.auth.models import Group


from .models import *


class SchoolFilter(django_filters.FilterSet):

    school = ModelChoiceFilter(
            field_name="user__profile__school__name",  # Use the profile relation to access the school
            label='School',
            queryset=School.objects.filter(active=True)
        )

