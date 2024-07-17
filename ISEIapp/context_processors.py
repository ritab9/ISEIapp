from teachercert.models import SchoolYear


def current_school_year_processor(request):
    if request.user.is_authenticated:
        try:
            school =request.user.teacher.school
            current_school_year=school.current_school_year
        except AttributeError:
            current_school_year = SchoolYear.objects.filter(current_school_year=True).first()
    else:
        current_school_year = SchoolYear.objects.filter(current_school_year=True).first()

    return {'current_school_year': current_school_year} or {}
