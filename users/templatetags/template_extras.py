from django import template
from selfstudy.models import StandardizedTestSession, StandardizedTestScore
import os
register = template.Library()

@register.filter
def add(value, arg):
    """Add a value to the argument."""
    try:
        return (value or 0) + (arg or 0)
    except TypeError:
        return ''

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
def get_item(obj, key):
    try:
        if isinstance(obj, dict):
            return obj.get(key)
        return obj[key]  # works for lists, tuples, and strings
    except (KeyError, IndexError, TypeError):
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

@register.filter
def is_on_team(accreditation, user):
    return accreditation.is_user_on_team(user)


from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta


@register.filter
def apr_status(submitted_at):
    today = date.today()
    due_date = date(today.year, 5, 1)

    green_threshold = due_date - relativedelta(months=2)  # March 1
    yellow_ex_threshold = due_date - relativedelta(months=4)  # Jan 1
    red_ex_threshold = due_date - relativedelta(years=1)  # May 1 last year
    late_threshold = due_date + relativedelta(weeks=2)  # May 15

    if submitted_at is None:
        return '‼️❗'

    # normalize to date
    if hasattr(submitted_at, 'date'):
        submitted_at = submitted_at.date()

    if submitted_at > late_threshold:
        return '🔴'
    elif submitted_at > due_date:
        return '🟡'
    elif submitted_at >= green_threshold:
        return '🟢'
    elif submitted_at >= yellow_ex_threshold:
        return '🔶'
    elif submitted_at >= red_ex_threshold:
        return '❗'
    else:
        return '‼️'