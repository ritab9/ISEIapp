from teachercert.models import SchoolYear


def current_school_year_processor(request):
    current_school_year = SchoolYear.objects.filter(current_school_year=True).first()
    return {'current_school_year': current_school_year}
