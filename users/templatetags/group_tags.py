from django import template
from users.myfunctions import *

register = template.Library()

@register.filter('in_group')
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter('certified_tag')
def certified_tag(user):
    teacher = Teacher.objects.get(user=user)
    return certified(teacher)

@register.filter('expired_certified_tag')
def expired_certified_tag(user):
    teacher = Teacher.objects.get(user=user)
    return expired_certified(teacher)