from django import template

register = template.Library()


@register.filter
def getattribute(value, arg):
    return getattr(value, arg)

@register.filter
def get_from_dict(dictionary, key):
    return dictionary.get(key)
