from teachercert.models import SchoolYear
from users.forms import SchoolYearForm


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

def navbar_schoolyear_form_processor(request):
    if request.user.is_authenticated:
        try:
            current_school_year = request.user.teacher.school.current_school_year
        except AttributeError:
            current_school_year = SchoolYear.objects.get(current_school_year=True)
        form = SchoolYearForm(initial={'school_year': current_school_year})
    else:
        form = None
    return {'navbar_schoolyear_form': form}