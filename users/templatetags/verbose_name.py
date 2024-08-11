from django import template
from django.core.exceptions import FieldDoesNotExist

register = template.Library()


@register.filter
def verbose_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    try:
        return instance._meta.get_field(field_name).verbose_name
    except FieldDoesNotExist:
        return None
