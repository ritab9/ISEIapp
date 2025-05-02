from django import template
from selfstudy.models import StandardizedTestSession, StandardizedTestScore
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
    if dictionary and isinstance(dictionary, dict):
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


@register.filter(name='get_score')
def get_score(score_map, value):
    """Custom filter to get the score from the score_map."""
    # Split the value by '-' to extract session_id, subject, and grade
    session_id, subject, grade = value.split("-")
    session_id = int(session_id)  # Convert to integer
    grade = int(grade)  # Convert grade to integer if it's stored as an integer

    # Check if the session, subject, and grade exist in the score_map and return the score
    if session_id in score_map and subject in score_map[session_id] and grade in score_map[session_id][subject]:
        return score_map[session_id][subject][grade]
    return None

