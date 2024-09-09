from django import template
import os
register = template.Library()


@register.filter
def get_attribute(value, arg):
    return getattr(value, arg)

@register.filter
def get_from_dict(dictionary, key):
    return dictionary.get(key)

@register.filter
def filename(value):
    return os.path.basename(value)