from django.db.models import Count
from users.models import Country
from .models import Student
from django.db.models import Q
from math import log10, ceil


def update_student_country_occurences(annual_report):
    # Students who potentially changed
    students_changed = Student.objects.filter(annual_report=annual_report)

    previous_year = annual_report.school_year.get_previous_school_year()

    # All students for the count
    if previous_year:
        # Only current SchoolYear or SchoolYear before
        students = Student.objects.filter(Q(annual_report__school_year=annual_report.school_year) |
                                          Q(annual_report__school_year=previous_year))
    else:
        # If there is no previous year, we only consider the current year
        students = Student.objects.filter(annual_report__school_year=annual_report.school_year)

    # Get countries ID belonging to students that have possibly changed
    changed_country_ids = students_changed.values_list('country_id', flat=True)

    # Consider only countries that belong to students that have possibly changed
    countries = students.filter(country_id__in=changed_country_ids).values('country_id') \
        .annotate(student_count=Count('country_id'))

    for country_data in countries:
        country_id = country_data['country_id']
        student_count = country_data['student_count']

        # you could also use get_queryset method to get a different set of students
        country = Country.objects.get(id=country_id)

        if country.student_occurrence != student_count:
            country.student_occurrence = student_count
            country.student_occurrence_log = ceil(log10(student_count)) if student_count > 0 else 0            # only one db call if value has changed
            country.save()
