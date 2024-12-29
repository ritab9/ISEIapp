from django import template
from services.models import Resource

register = template.Library()

@register.simple_tag
def get_resource_by_name(name):
    return Resource.objects.filter(name=name).first()
