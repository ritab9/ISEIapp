import django_filters
from django_filters import ModelChoiceFilter
from django.contrib.auth.models import Group


from users.models import School


class UserFilter(django_filters.FilterSet):
    school = ModelChoiceFilter(field_name="teacher__user__profile__school__name", label='School', queryset= School.objects.filter(active=True) )
    group = ModelChoiceFilter(field_name="groups", label='Group', queryset=Group.objects.all() )
