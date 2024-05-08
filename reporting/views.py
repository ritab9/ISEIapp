
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import AnnualReport, Report, School, SchoolYear, Student
from .forms import StudentForm
from django.contrib import messages


# Create your views here.

def student_report(request, schoolID, school_yearID):
    report = get_object_or_404(Report, name="Student Enrollment Report")
    school = get_object_or_404(School, id=schoolID)
    school_year = get_object_or_404(SchoolYear, id=school_yearID)

    annual_report, created = AnnualReport.objects.get_or_create(
        school=school,
        school_year=school_year,
        report=report
    )

    if school.address.country.code == "USA":
        if school.address.state_us == "TN":
            StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=1, can_delete=True,
                                              exclude=('annual_report', 'id', 'age_at_registration'))
        else:
            StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=1, can_delete=True,
                                                  exclude=('annual_report', 'id', 'age_at_registration', 'TN_county'))
    else:
        StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=1, can_delete=True,
                                              exclude=('annual_report', 'id', 'age_at_registration', 'us_state',
                                                       'TN_county'))

    if request.method == 'POST':
        formset = StudentFormSet(request.POST, queryset=Student.objects.filter(annual_report=annual_report))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.annual_report = annual_report
                print(instance)
                instance.save()

            if 'submit' in request.POST:
                # If the 'Submit' button is clicked, redirect to a principal dashboard
                return redirect('principal_dashboard', request.user.id)
            elif 'save_and_add_more' in request.POST:
                # If the 'Save and add more' button is clicked, redirect back to the same page
                return redirect(request.path)
        #else:
        #    messages.error(request, 'Some forms contain errors. Please correct them and try again.')

    else:
        formset = StudentFormSet(queryset=Student.objects.filter(annual_report=annual_report))

    context = dict(formset=formset)

    return render(request, 'student_report.html', context)

def opening_report(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'opening_report.html')

def day190_report(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'day190_report.html')

def employee_report(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'employee_report.html')

def inservice_report(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'inservice_report.html')

def ap_report(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'student_report.html')
    
