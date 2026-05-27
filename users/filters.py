import django_filters
from django_filters import DateFilter, CharFilter, ChoiceFilter, BooleanFilter, ModelChoiceFilter
from django.contrib.auth.models import Group


from .models import *


#class SchoolFilter(django_filters.FilterSet):

#    school = ModelChoiceFilter(
#            field_name="user__profile__school__name",  # Use the profile relation to access the school
#            label='School',
#            queryset=School.objects.filter(active=True)
#        )

class SchoolFilter(django_filters.FilterSet):

    school = ModelChoiceFilter(
        label='School',
        queryset=School.objects.filter(active=True),
        method='filter_school'
    )

    def filter_school(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(user__profile__school=value) |
            Q(user__memberships__school=value)
        ).distinct()