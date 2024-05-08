
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import AnnualReport, ReportType, School, SchoolYear, Student
from .forms import StudentForm
from datetime import date
from django.contrib import messages


# Create your views here.

def student_report(request, schoolID, school_yearID):
    report_type = get_object_or_404(ReportType, name="Student Enrollment Report")
    school = get_object_or_404(School, id=schoolID)
    school_year = get_object_or_404(SchoolYear, id=school_yearID)

    annual_report, created = AnnualReport.objects.get_or_create(
        school=school,
        school_year=school_year,
        report_type=report_type
    )

    if school.address.country.code == "USA":
        if school.address.state_us == "TN":
            StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=0, can_delete=True,
                                              exclude=('annual_report', 'id', 'age_at_registration'))
        else:
            StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=0, can_delete=True,
                                                  exclude=('annual_report', 'id', 'age_at_registration', 'TN_county'))
    else:
        StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=0, can_delete=True,
                                              exclude=('annual_report', 'id', 'age_at_registration', 'us_state',
                                                       'TN_county'))

    if request.method == 'POST':
        formset = StudentFormSet(request.POST, queryset=Student.objects.filter(annual_report=annual_report))
        for form in formset:
            if form.has_changed():
                print("Following fields in the form were changed:", form.changed_data)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.annual_report = annual_report
                instance.save()

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                    annual_report.save()
                annual_report.last_update_date = date.today()
                annual_report.save()
                #Todo Send email to ISEI about it's commpletion
                return redirect('principal_dashboard', request.user.id)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()
                #annual_report.submit_date = None
                #annual_report.save()
                return redirect('principal_dashboard', request.user.id)

    else:
        formset = StudentFormSet(queryset=Student.objects.filter(annual_report=annual_report))

    context = dict(formset=formset, annual_report=annual_report)

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
    
