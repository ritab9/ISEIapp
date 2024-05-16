from django import template
from users.myfunctions import *

register = template.Library()

@register.filter('in_group')
def in_group(user, group_names):
    group_names = group_names.split(',')
    return user.groups.filter(name__in=group_names).exists()

@register.filter('certified_tag')
def certified_tag(user):
    teacher = Teacher.objects.get(user=user)
    return certified(teacher)

@register.filter('expired_certified_tag')
def expired_certified_tag(user):
    teacher = Teacher.objects.get(user=user)
    return expired_certified(teacher)

@register.filter('application_submitted_tag')
def application_submitted_tag(user):
    teacher = Teacher.objects.get(user=user)
    return application_submitted(teacher)