from django.shortcuts import render, redirect, get_object_or_404
from .models import StudentInfo, StudentReport
from .forms import StudentInfoFormSet
from users.models import School
from teachercert.models import SchoolYear
from .filters import StudentInfoFilter


def student_report(request, school_id=1, school_year_id=1):

    school = get_object_or_404(School, pk=school_id)
    school_year = get_object_or_404(SchoolYear, id=school_year_id)

    report, created = StudentReport.objects.get_or_create(school_id=school_id, school_year_id=school_year_id)
    students = report.students.all().order_by('grade', 'last_name')

    # Create an instance of the filter and pass the queryset
    student_filter = StudentInfoFilter(request.GET, queryset=students)

    students = student_filter.qs

    if request.method == 'POST':
        # Process form data and create a new student
        # Assuming you have a StudentForm for creating new students
        formset = StudentInfoFormSet(request.POST)
        instances_to_save = []
        for form in formset:
            if form.has_changed() or form.instance.pk:
                if form.is_valid():
                    instances_to_save.append(form.instance)


        if instances_to_save:
            for instance in instances_to_save:
                instance.save()
                report.students.add(instance)
            return redirect('student_report', school_id, school_year_id)  # go back to CEUdashboard

    else:
        formset = StudentInfoFormSet()

    context = {
        'school': school,
        'school_year': school_year,
        'students': students,
        'formset': formset,
        'student_filter':student_filter,
    }
    return render(request, 'student_report.html', context)





def student_report_view(request, school_id=1, school_year_id=1):

    school = get_object_or_404(School, pk=school_id)
    school_year = get_object_or_404(SchoolYear, id=school_year_id)

    report, created = StudentReport.objects.get_or_create(school_id=school_id, school_year_id=school_year_id)
    students = report.students.all().order_by('grade', 'last_name')

    # Create an instance of the filter and pass the queryset
    student_filter = StudentInfoFilter(request.GET, queryset=students)

    students = student_filter.qs

    context = {
        'school': school,
        'school_year': school_year,
        'students': students,
        'student_filter':student_filter,
    }
    return render(request, 'student_report_view.html', context)