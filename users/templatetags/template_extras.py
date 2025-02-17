from django import template
import os
register = template.Library()

@register.filter
def add(value, arg):
    """Add a value to the argument."""
    return value + arg

@register.filter
def modulus(value, arg):
    """Apply modulus operation."""
    return value % arg

@register.filter
def get_attribute(value, arg):
    return getattr(value, arg)

@register.filter
def get_from_dict(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item(list_, index):
    try:
        return list_[index]
    except IndexError:
        return None

@register.filter
def filename(value):
    return os.path.basename(value)