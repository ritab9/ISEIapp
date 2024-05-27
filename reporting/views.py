
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from django.forms import modelformset_factory
from .models import AnnualReport, ReportType, School, SchoolYear, Student, TNCounty, Country, StateField
from .forms import StudentForm, UploadFileForm
from datetime import date, timedelta
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
import numpy as np

from django.db.models import Q

from django.http import FileResponse
from django.views import View
from io import BytesIO
from django.contrib.auth.decorators import login_required
from reporting.models import GRADE_LEVEL_DICT
from .filters import *
from django.db import transaction



def report_dashboard(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'report_dashboard.html')

#Student Report Views
def student_report(request,arID):

    annual_report = AnnualReport.objects.select_related('school__address__country').get(id=arID)
    school = annual_report.school

    exclude_fields = ['annual_report', 'id', 'age_at_registration']
    if school.address.country.code != "US" or school.address.state_us != "TN":
        exclude_fields.append('TN_county')

    if school.address.country.code != "US":
        exclude_fields.append('us_state')

    StudentFormSet = modelformset_factory(Student, form=StudentForm, extra=1, can_delete=True, exclude=exclude_fields)

    if request.method == 'POST':
        formset = StudentFormSet(request.POST, queryset=Student.objects.filter(annual_report=annual_report))
        if formset.is_valid():
            if formset.has_changed():
                for form in formset:
                    print(f'Changed fields for form {form.instance.pk}:', form.changed_data)
                    if form.has_changed():
                        if form.instance.pk is not None:
                            form.save()
                        else:
                            instance=form.save(commit=False)
                            instance.annual_report = annual_report
                            instance.save()
                for form in formset.deleted_forms:
                    form.instance.delete()

            #for object in formset.deleted_objects:
            #    object.delete()

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                    annual_report.save()
                annual_report.last_update_date = date.today()
                annual_report.save()
                #Todo Send email to ISEI about it's completion
                return redirect('principal_dashboard', request.user.teacher.school.id)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()
                #annual_report.submit_date = None
                #annual_report.save()
                return redirect('principal_dashboard', request.user.teacher.school.id)

    else:
        if annual_report.submit_date:
            students_qs = (Student.objects.filter(annual_report=annual_report, status='enrolled')
                           .select_related('country', 'TN_county')
                           .order_by('grade_level', 'name'))
        else:
            students_qs = (Student.objects.filter(annual_report=annual_report)
                           .select_related('country', 'TN_county')
                           .order_by('grade_level', 'name'))
        formset = StudentFormSet(queryset=students_qs)

    context = dict(formset=formset, annual_report=annual_report)
    return render(request, 'student_report.html', context)

def import_students_prev_year(request, arID):
    report = get_object_or_404(AnnualReport, id=arID)
    prev_school_year = report.school_year.get_previous_school_year()

    if not prev_school_year:
        messages.error(request, 'No previous school year found.')
        return redirect('student_report' , arID)  # Update this with where you want to redirect

    prev_report = AnnualReport.objects.filter(school=report.school, school_year=prev_school_year,
                                              report_type=report.report_type).first()

    if not prev_report:
        messages.error(request, 'No previous report found.')
        return redirect('student_report', arID)  # Update this with where you want to redirect

    students_to_import = Student.objects.filter(annual_report=prev_report, status='enrolled')

    # Now copy over all students
    imported_count = 0
    for student in students_to_import:
        if Student.objects.filter(name=student.name, annual_report=report).exists():
            continue
        student.pk = None  # Makes Django create a new instance
        student.annual_report = report
        if student.age:
            student.age += 1
        # Handle grade level (assuming it's not None, add error handling as needed)
        student.grade_level = student.grade_level + 1 if student.grade_level < 13 else 13
        # Registration date. Make sure to handle None case if needed
        student.registration_date = student.registration_date + timedelta(days=365)
        student.save()
        imported_count += 1  # increment the count of imported students

    messages.success(request, '{} Students imported successfully.'.format(imported_count))
    return redirect('student_report', arID)  # Update this with where you want to redirect after success


def student_report_display(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    if annual_report.submit_date:
        students = Student.objects.filter(annual_report=annual_report, status = "enrolled").select_related('annual_report', 'country',
                                                                                  'TN_county').order_by('grade_level', 'name')
    else:
        students = Student.objects.filter(annual_report=annual_report).select_related('annual_report', 'country',
                                                                                      'TN_county').order_by('grade_level', 'name')

    filter_form = StudentFilterForm(request.GET or None, annual_report=annual_report)


    if request.GET:
        if filter_form.is_valid():
            if 'grade_level' in filter_form.cleaned_data and filter_form.cleaned_data['grade_level']:
                students = students.filter(grade_level=filter_form.cleaned_data['grade_level'])

            if 'status' in filter_form.cleaned_data and filter_form.cleaned_data['status']:
                students = students.filter(status=filter_form.cleaned_data['status'])

            if 'location' in filter_form.cleaned_data and filter_form.cleaned_data['location']:
                students = students.filter(location=filter_form.cleaned_data['location'])

            if 'gender' in filter_form.cleaned_data and filter_form.cleaned_data['gender']:
                students = students.filter(gender=filter_form.cleaned_data['gender'])

            if 'country' in filter_form.cleaned_data and filter_form.cleaned_data['country']:
                students = students.filter(country=filter_form.cleaned_data['country'])

            if 'us_state' in filter_form.cleaned_data and filter_form.cleaned_data['us_state']:
                students = students.filter(us_state=filter_form.cleaned_data['us_state'])

            if 'TN_county' in filter_form.cleaned_data and filter_form.cleaned_data['TN_county']:
                students = students.filter(TN_county=filter_form.cleaned_data['TN_county'])


    context = {
        'annual_report': annual_report,
        'students': students,
        'filter_form': filter_form,
    }
    return render(request, 'student_report_display.html', context)

class StudentExcelDownload(View):
    def get(self, request, *args, **kwargs):
        #TODO take out age; it's only for importing old data (or maybe keep it as an alternative to birth_date?)
        address = request.user.teacher.school.address
        if address.state_us == "TN":
            column_headers = ['name', 'gender', 'grade_level', 'age',  'birth_date', 'address', 'us_state', 'TN_county', 'country',
                          'registration_date',  'withdraw_date', 'status', 'location','baptized', 'parent_sda',
                          ]
        elif address.country.code == "US":
            column_headers = ['name', 'gender', 'grade_level', 'age', 'birth_date', 'address', 'us_state', 'country',
                              'registration_date', 'withdraw_date', 'status', 'location', 'baptized', 'parent_sda',
                              ]
        else:
            column_headers = ['name', 'gender', 'grade_level', 'age', 'birth_date', 'address', 'country',
                              'registration_date', 'withdraw_date', 'status', 'location', 'baptized', 'parent_sda',
                              ]

        df = pd.DataFrame(columns=column_headers)

        # Create a BytesIO buffer to hold the excel file in-memory
        buf = BytesIO()

        # Save the new DataFrame to the buffer
        df.to_excel(buf, index=False)

        # Rewind the buffer to start
        buf.seek(0)

        # Create a Fileresponse object using the buffer contents
        response = FileResponse(buf, as_attachment=True, filename='Student_data_template.xlsx')
        return response

#import student from Excel
def student_import_dashboard(request, arID):

    annual_report_instance = AnnualReport.objects.get(id=arID)
    school_state = annual_report_instance.school.address.state_us

    valid_state_codes = [code for code, state in StateField.STATE_CHOICES]
    valid_choices = ['Y', 'N', 'U']
    valid_statuses = ['enrolled', 'graduated', 'did_not_return']
    valid_locations = ['on-site', 'satellite', 'distance-learning']
    valid_gender = ['M', 'F']
    valid_boarding_choices = {'Yes': True, 'No': False}

    today = pd.to_datetime(date.today())
    one_year_ago = today - pd.DateOffset(years=1)
    twenty_five_years_ago = today - pd.DateOffset(years=25)
    three_years_ago = pd.to_datetime(date.today()) - pd.DateOffset(years=3)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = pd.read_excel(request.FILES['file'])
            data = data.replace({np.nan: None})

            created_count = 0  # initialize counter

            for index, row in data.iterrows():

                #validate row
                # name validation
                name = row['name']
                if pd.isna(name) or not isinstance(name, str) or len(name) > 200:
                    messages.error(request, f"In row {index + 1}, {name} field is not a valid name. No data is saved for this row")
                    continue
                # address validation
                address = row['address']
                if pd.isna(address) or not isinstance(address, str) or len(address) > 500:
                    messages.error(request, f"In row {index + 1}, {address} field is not a valid address. No data is saved for this row")
                    continue
                # country validation
                try:
                    country_instance = Country.objects.get(Q(code=row['country']) | Q(name=row['country']))
                except Country.DoesNotExist:
                    messages.error(request, f"In row {index + 1}, '{row['country']}' is not a valid country name or code. No data is saved for this row")
                    continue
                # validate US state when the country code is 'US', and TN_state when state is TN
                us_state = None
                tn_county_instance = None
                if country_instance.code == 'US':
                    us_state = row['us_state']
                    if us_state not in valid_state_codes:
                        messages.error(request, f"In row {index + 1}, '{us_state}' is not a valid US state code. No data is saved for this row")
                        continue
                    else:
                        if school_state=='TN' and us_state == 'TN':
                            try:
                                tn_county_instance = TNCounty.objects.get(name=row['TN_county'])
                            except TNCounty.DoesNotExist:
                                messages.error(request,f"In row {index + 1}, {row['TN_county']}' is not a valid TN county code. No data is saved for this row")
                                continue


                # TODO Here Age is required, combine it with birth_date validation
                # Check if age is not a number or if it falls outside the range 3-25
                age = row['age']
                if pd.isna(age):
                    messages.error(request, f"In row {index + 1}, 'age' is missing. No data is saved for this row")
                    continue
                else:
                    age = int(row['age'])
                    if not 3 <= age <= 25:
                        messages.error(request,
                                       f"In row {index + 1}, {age} is not a valid age. No data is saved for this row")
                        continue

                # validate birth date
                birth_date = pd.to_datetime(row['birth_date'], errors='coerce') if pd.notnull(
                    row['birth_date']) else None
                if not age:
                    if birth_date is None or not twenty_five_years_ago <= birth_date <= one_year_ago:
                            messages.error(request,f"Invalid Birth Date {birth_date} at row: {index+1}")
                            continue

                # validate registration and withdraw date
                registration_date = pd.to_datetime(row['registration_date'], errors='coerce') if pd.notnull(
                    row['registration_date']) else None
                if registration_date is None or registration_date < three_years_ago:
                        messages.error(request, f"Invalid Registration Date {registration_date} at row: {index+1}")
                        continue

                # Parse and validate withdraw_date
                withdraw_date = pd.to_datetime(row['withdraw_date'], errors='coerce') if pd.notnull(
                    row['withdraw_date']) else None
                if withdraw_date is not None:
                    if withdraw_date < three_years_ago:
                        messages.error(request, f"Invalid Withdraw Date {withdraw_date} at row: {index+1}")
                        continue

                # Validate 'baptized'
                baptized = row.get('baptized')
                if baptized is None:
                    baptized = 'U'
                if baptized not in valid_choices:
                    messages.error(request, f" {baptized} is an invalid value for 'baptized' at row: {index+1} (valid_choices = ['Y', 'N'])")
                    continue

                # Validate 'parent_sda'
                parent_sda = row.get('parent_sda')
                if parent_sda is None:
                    parent_sda = 'U'
                if parent_sda not in valid_choices:
                    messages.error(request, f" {parent_sda} is invalid value for 'parent_sda' at row: {index+1} (valid_choices = ['Y', 'N'])")
                    continue

                #validate gender
                gender=row.get('gender')
                if gender is not None and gender not in valid_gender:
                    messages.error(request, f"Invalid gender {gender} at row: {index+1}")
                    continue

                # Validate enrollment status
                status = row.get('status')
                if status is None:
                    status = 'enrolled'
                if status not in valid_statuses:
                    messages.error(request, f"Invalid status {status} at row: {index+1}")
                    continue

                # Validate 'grade_level'
                grade_level_str = str(row.get('grade_level'))
                if grade_level_str is None or grade_level_str not in GRADE_LEVEL_DICT:
                    messages.error(request, f"Invalid or missing grade level {grade_level_str} at row: {index+1}")
                    continue
                grade_level = GRADE_LEVEL_DICT[grade_level_str]

                # Validate 'location'
                location = row.get('location')
                if location is None:
                    location = 'on-site'
                if location not in valid_locations:
                    messages.error(request, f"Invalid location at row: {index+1}")
                    continue

                #validate 'boarding'
                try:
                    # Attempt to map the boarding value to a boolean
                    boarding = valid_boarding_choices[row['boarding']]
                except KeyError:
                    boarding = False
                    #messages.error(request, f'Invalid boarding value at row {index + 1} in the Excel file.')
                    #continue  # Skip to next iteration

                # Create or update instance
                student, created = Student.objects.update_or_create(
                    name=name,
                    birth_date=birth_date,
                    defaults = {
                        'address': address,
                        'us_state': us_state,
                        'TN_county': tn_county_instance,
                        'country': country_instance,
                        'gender': gender,
                        'boarding':boarding,
                        'baptized': baptized,
                        'parent_sda': parent_sda,
                        'status': status,
                        'age':age,
                        'grade_level': grade_level,
                        'registration_date': registration_date,
                        'withdraw_date': withdraw_date,
                        'location': location,
                        'annual_report': annual_report_instance
                    }
                )
                if created:
                    created_count += 1

            if created_count > 0:
                messages.success(request,f"{created_count} student record(s) have been imported.")
            else:
                messages.info(request,f"No student record(s) have been imported. The data is either incomplete or the students are already registered in this report.")

    else:
        form = UploadFileForm()
    return render(request, 'student_import_dashboard.html', {'form': form, 'annual_report': annual_report_instance})


def opening_report(request, arID):
    # Add your processing here
    return render(request, 'opening_report.html')
def opening_report_display(request, arID):
    # Add your processing here
    return render(request, 'opening_report_display.html')


def day190_report(request, arID):
    # Add your processing here
    return render(request, 'day190_report.html')
def day190_report_display(request, arID):
    # Add your processing here
    return render(request, 'day190_report_display.html')

def employee_report(request, arID):
    # Add your processing here
    return render(request, 'employee_report.html')
def employee_report_display(request, arID):
    # Add your processing here
    return render(request, 'employee_report_display.html')

def inservice_report(request, arID):
    # Add your processing here
    return render(request, 'inservice_report.html')
def inservice_report_display(request, arID):
    # Add your processing here
    return render(request, 'inservice_report_display.html')

def ap_report(request, arID):
    # Add your processing here
    return render(request, 'ap_report.html')
def ap_report_display(request, arID):
    # Add your processing here
    return render(request, 'ap_report_display.html')
    
