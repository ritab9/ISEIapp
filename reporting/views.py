
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse

from django.forms import modelformset_factory
from django.db.models import Sum
from .forms import *
from datetime import date, timedelta
from django.contrib import messages
from django.db import transaction

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
from django.db.models import Prefetch, Max


from users.models import AccreditationInfo
from .functions import update_student_country_occurences
from teachercert.myfunctions import newest_certificate
from django.db import IntegrityError


#individual school reports
@login_required(login_url='login')
def report_dashboard(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'report_dashboard.html')

#Student Report Views
@login_required(login_url='login')
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
                    if form.has_changed():
                        if form.instance.pk is not None:
                            form.save()
                        else:
                            instance=form.save(commit=False)
                            instance.annual_report = annual_report
                            instance.save()
                for form in formset.deleted_forms:
                    form.instance.delete()

            update_student_country_occurences(annual_report)

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                annual_report.last_update_date = date.today()
                annual_report.save()
                #Todo Send email to ISEI about it's completion
                return redirect('school_dashboard', school.id)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()

                return redirect('school_dashboard', school.id)


    else:
        if annual_report.submit_date:
            students_qs = (Student.objects.filter(annual_report=annual_report,  status__in=['enrolled', 'withdrawn', 'part-time'])
                           .select_related('country', 'TN_county')
                           .order_by('status','grade_level', 'name'))
        else:
            students_qs = (Student.objects.filter(annual_report=annual_report)
                           .select_related('country', 'TN_county')
                           .order_by('grade_level', 'name'))
        formset = StudentFormSet(queryset=students_qs)

    context = dict(formset=formset, annual_report=annual_report)
    return render(request, 'student_report.html', context)

@login_required(login_url='login')
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

    students_to_import = Student.objects.filter(annual_report=prev_report, status__in=['enrolled','part-time'])

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
        if student.grade_level < 13:
            student.registration_date = student.registration_date + timedelta(days=365)
        else:
            student.status="graduated"
        student.save()
        imported_count += 1  # increment the count of imported students

    messages.success(request, '{} Students imported successfully.'.format(imported_count))
    return redirect('student_report', arID)  # Update this with where you want to redirect after successLEt me


@login_required(login_url='login')
def student_report_display(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    students = Student.objects.filter(annual_report=annual_report).select_related('annual_report', 'country',
                                                                                 'TN_county').order_by('grade_level', 'name')
    #students = Student.objects.filter(annual_report=annual_report, status__in=['enrolled','part-time','withdrawn']).select_related('annual_report', 'country',
                                                                                      #'TN_county').order_by('grade_level', 'name')

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
@login_required(login_url='login')
def student_import_dashboard(request, arID):

    annual_report_instance = AnnualReport.objects.get(id=arID)
    school_state = annual_report_instance.school.address.state_us

    valid_state_codes = [code for code, state in StateField.STATE_CHOICES]
    valid_choices = ['Y', 'N', 'U']
    valid_statuses = ['enrolled', 'part-time', 'graduated', 'did_not_return']
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

@login_required(login_url='login')
def tn_student_export(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    date=annual_report.last_update_date
    school= annual_report.school
    school_name = school.name
    address=school.address
    school_address = address.address_1
    school_city = address.city
    school_zip = address.zip_code
    school_state = address.state_us
    school_country = address.country
    school_phone= school.phone_number
    school_email = school.email
    school_principal = school.principal

    accreditations = AccreditationInfo.objects.filter(school=school)

    # extract agency from each accreditation
    agencies = [accreditation.agency.abbreviation for accreditation in accreditations]
    agencies_string = ', '.join(agencies)


    students = Student.objects.filter(annual_report=annual_report, status__in = ["enrolled"]).select_related('country',
                                                                                 'TN_county').order_by('grade_level', 'name')
    no_students = len(students)

    # Create DataFrame with school's info
    data = {'Date': [date],
            'Name of School': [school_name],
            'Principal or Headmaster': [school_principal],
            'Address': [school_address],
            'City': [school_city],
            'ZIP': [school_zip],
            'State': [school_state],
            'Country': [school_country],
            'Phone': [school_phone],
            'Email': [school_email],
            'Member Association': [agencies_string],
            'Number of pupils enrolled': [no_students]}

    school_df = pd.DataFrame(data)

    student_df=pd.DataFrame.from_records(students.values(
        'name', 'age_at_registration', 'grade_level', 'address', 'us_state', 'TN_county__name', 'country__name',
        'registration_date', 'withdraw_date', 'location',
    ))

    student_df[['address', 'us_state', 'country__name']] = student_df[['address', 'us_state', 'country__name']].fillna('')
    student_df['address'] = student_df['address'] + ' ' + student_df['us_state'] + ' ' + student_df['country__name']

    student_df = student_df.drop(columns=['us_state', 'country__name'])

    # Write dataframe to an excel object in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        school_df.to_excel(writer, sheet_name="School Info", index=False)
        student_df.to_excel(writer, sheet_name="Student Info", index=False)


    # Set the output's file pointer to the beginning
    output.seek(0)

    # Create a response with the xlsx file
    response = HttpResponse(output.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    filename = "StudentReport.xlsx"
    # Specify the filename; this will appear when user is saving the file
    response['Content-Disposition'] = "attachment; filename=" + filename

    return response



#190 Day Report views
@login_required(login_url='login')
def day190_report(request, arID):
    annual_report = AnnualReport.objects.get(id=arID)

    day190, created = Day190.objects.get_or_create(annual_report=annual_report)

    VacationFormSet = modelformset_factory(Vacations, form=VacationsForm, extra=1, can_delete=True)
    InserviceFormSet = modelformset_factory(InserviceDiscretionaryDays, form=InserviceDiscretionaryDaysForm, extra=1, can_delete=True)
    AbbreviatedFormSet = modelformset_factory(AbbreviatedDays, form=AbbreviatedDaysForm, extra=1, max_num=3, can_delete=True)
    SundayFormSet = modelformset_factory(SundaySchoolDays, form=SundaySchoolDaysForm, extra=1, can_delete=True, formset=BaseSundaySchoolDaysFormSet)
    EnrichmentFormSet = modelformset_factory(EducationalEnrichmentActivity, form=EducationalEnrichmentActivityForm, extra=1, can_delete=True)

    errors=[]

    if request.method == 'POST':
        day190_form = Day190Form(request.POST, request.FILES or None, instance=day190)
        formset_vacation = VacationFormSet(request.POST, prefix='vacation')
        formset_inservice = InserviceFormSet(request.POST, prefix='inservice')
        formset_abbreviated = AbbreviatedFormSet(request.POST, prefix='abbreviated')
        formset_sunday = SundayFormSet(request.POST, prefix='sunday')
        formset_enrichment = EnrichmentFormSet(request.POST, prefix='enrichment')

        if day190_form.is_valid():
            day190 = day190_form.save(commit=False)
            day190.annual_report = annual_report
            day190.save()

            if formset_vacation.is_valid():
                instances = formset_vacation.save(commit=False)
                for instance in instances:
                    instance.day190 = day190
                    instance.save()
                for obj in formset_vacation.deleted_objects:
                    obj.delete()
            else:
                errors.append(formset_vacation.errors)

            if formset_inservice.is_valid():
                instances = formset_inservice.save(commit=False)
                for instance in instances:
                    instance.day190 = day190
                    instance.save()
                for obj in formset_inservice.deleted_objects:
                    obj.delete()
            else:
                errors.append(formset_inservice.errors)

            if formset_abbreviated.is_valid():
                instances = formset_abbreviated.save(commit=False)
                for instance in instances:
                    instance.day190 = day190
                    instance.save()
                for obj in formset_abbreviated.deleted_objects:
                    obj.delete()
            else:
                errors.append(formset_abbreviated.errors)

            if formset_sunday.is_valid():
                instances = formset_sunday.save(commit=False)
                for instance in instances:
                    instance.day190 = day190
                    instance.save()
                for obj in formset_sunday.deleted_objects:
                    obj.delete()
            else:
                errors.append(formset_sunday.errors)


            if formset_enrichment.is_valid():
                instances = formset_enrichment.save(commit=False)
                for instance in instances:
                    instance.day190 = day190
                    instance.save()
                for obj in formset_enrichment.deleted_objects:
                    obj.delete()

            else:
                errors.append(formset_enrichment.errors)

            if not errors:
                if 'submit' in request.POST:
                    if not annual_report.submit_date:
                            annual_report.submit_date = date.today()
                    annual_report.last_update_date=date.today()
                    annual_report.save()
                elif 'save'in request.POST:
                    annual_report.last_update_date = date.today()
                    annual_report.save()
                return redirect('school_dashboard', annual_report.school.id)

            else:
                errors.append(day190_form.errors)

    else:
        day190_form = Day190Form(instance=day190)
        formset_vacation = VacationFormSet(queryset=Vacations.objects.filter(day190=day190), prefix='vacation')
        formset_inservice = InserviceFormSet(queryset=InserviceDiscretionaryDays.objects.filter(day190=day190),
                                             prefix='inservice')
        formset_abbreviated = AbbreviatedFormSet(queryset=AbbreviatedDays.objects.filter(day190=day190),
                                                 prefix='abbreviated')
        formset_sunday = SundayFormSet(queryset=SundaySchoolDays.objects.filter(day190=day190),
                                                 prefix='sunday')
        formset_enrichment = EnrichmentFormSet(queryset=EducationalEnrichmentActivity.objects.filter(day190=day190),
                                                 prefix='enrichment')

    # Generate empty forms for the formsets
    empty_formset_vacation = VacationsForm(prefix='vacation')  # empty form for Vacations formset
    empty_formset_inservice = InserviceDiscretionaryDaysForm(prefix='inservice')  # empty form for Inservice formset
    empty_formset_abbreviated = AbbreviatedDaysForm(prefix='abbreviated')  # empty form for Abbreviated formset
    empty_formset_sunday = SundaySchoolDaysForm(prefix='sunday')  # empty form for Sunday formset
    empty_formset_enrichment = EnrichmentFormSet(prefix='enrichment')

    context = {
        'annual_report': annual_report,
        'errors':errors,
        'day190_form': day190_form,
        'formset_vacation': formset_vacation,
        'formset_inservice': formset_inservice,
        'formset_abbreviated': formset_abbreviated,
        'formset_sunday': formset_sunday,
        'formset_enrichment': formset_enrichment,
        'empty_formsets': [empty_formset_vacation, empty_formset_inservice, empty_formset_abbreviated, empty_formset_sunday, empty_formset_enrichment],
    }

    return render(request, 'day190_report.html', context)

@login_required(login_url='login')
def day190_report_display(request, arID):
    annual_report = get_object_or_404(AnnualReport, id=arID)
    try:
        day190_report = Day190.objects.get(annual_report=annual_report)
    except Day190.DoesNotExist:
        messages.error(request, 'Day190 Report not found for this Annual Report')
        return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))

    if day190_report is not None:
        vacations_report = Vacations.objects.filter(day190=day190_report)
        inservice_days_report = InserviceDiscretionaryDays.objects.filter(day190=day190_report)
        abbreviated_days_report = AbbreviatedDays.objects.filter(day190=day190_report)
        sunday_school_days_report = SundaySchoolDays.objects.filter(day190=day190_report)
        educational_enrichment_activities_report = EducationalEnrichmentActivity.objects.filter(day190=day190_report)

        total_inservice_discretionay_hours = sum(inservice_day.hours for inservice_day in inservice_days_report)

        discretionary_hours = inservice_days_report.filter(type='DS')
        total_discretionary_hours = sum(day.hours for day in discretionary_hours)

        total_inservice_hours = total_inservice_discretionay_hours - total_discretionary_hours

        sunday_school_days_count = sunday_school_days_report.count()

        educational_enrichment_days_total = educational_enrichment_activities_report.aggregate(total_days=Sum('days'))[
            'total_days']

        context = {
            'day190_report': day190_report,
            'vacations_report': vacations_report,
            'inservice_days_report': inservice_days_report,
            'abbreviated_days_report': abbreviated_days_report,
            'sunday_school_days_report': sunday_school_days_report,
            'educational_enrichment_activities_report': educational_enrichment_activities_report,
            'total_inservice_hours': total_inservice_hours,
            'total_inservice_dictionary_hours': total_inservice_discretionay_hours,
            'sunday_school_days_count': sunday_school_days_count,
            'educational_enrichment_days_total':educational_enrichment_days_total,
            'arID': arID,
        }
        return render(request, 'day190_report_display.html', context)

@login_required(login_url='login')
def employee_report(request, arID):
    all_personnel = Personnel.objects.filter(annual_report__id=arID).exclude(status=StaffStatus.NO_LONGER_EMPLOYED).select_related('teacher', 'annual_report').prefetch_related(
        'positions', 'degrees', 'subjects_teaching', 'subjects_taught').order_by('last_name')
    annual_report = get_object_or_404(AnnualReport, id=arID)
    school=annual_report.school.abbreviation

    admin_positions = StaffPosition.objects.filter(category=StaffCategory.ADMINISTRATIVE)
    teaching_positions = StaffPosition.objects.filter(category=StaffCategory.TEACHING)
    general_positions = StaffPosition.objects.filter(category=StaffCategory.GENERAL_STAFF)


    context={'arID':arID}
    personnel_groups = []
    processed_personnel = set()  # keep track of processed personnel

    for group, positions, code in (
            ('Admin Personnel', admin_positions, 'A'),
            ('Teaching Personnel', teaching_positions, 'T'),
            ('General Personnel', general_positions, 'G'),
    ):
        group_personnel_list = []
        for p in all_personnel:
            if p in processed_personnel:  # check if personnel has been processed
                continue  # skip to next iteration if personnel already processed
            if set(p.positions.all()).intersection(positions):
                personnel_dict = {'personnel': p,}
                # Add teacher info if available
                if p.teacher:
                    newest_cert = newest_certificate(p.teacher)
                    if newest_cert:
                        endorsements = newest_cert.tendorsement_set.all()
                        endorsements_list = [e.endorsement.name for e in endorsements]

                        personnel_dict['certification_type'] = newest_cert.certification_type
                        personnel_dict['renewal_date'] = newest_cert.renewal_date
                        personnel_dict['endorsements'] = endorsements_list
                group_personnel_list.append(personnel_dict)
                processed_personnel.add(p)  # add personnel to set of processed_personnel

        personnel_groups.append({'group_name': group, 'group_personnel': group_personnel_list, 'code':code })

    if request.method == 'POST':
        if 'complete' in request.POST:
            if not annual_report.submit_date:
                annual_report.submit_date = date.today()
            annual_report.last_update_date = date.today()
            annual_report.save()
        elif 'save' in request.POST:
            annual_report.last_update_date = date.today()
            annual_report.save()
        return redirect('school_dashboard', annual_report.school.id)

    context['personnel_groups'] = personnel_groups
    context['arID'] = arID
    context['map'] = CATEGORY_EXPLANATION_MAP
    context['school']=school
    context['school_year']=annual_report.school_year

    return render(request, 'employee_report.html', context)


@login_required(login_url='login')
def employee_add_edit(request, arID, personnelID=None, positionCode=None):
    annual_report = get_object_or_404(AnnualReport, id=arID)
    school = get_object_or_404(School, id=annual_report.school_id)

    subject_categories = {
        "B": {"name": "Bible", "subjects": []},
        "C": {"name": "Computer/Tech", "subjects": []},
        "F": {"name": "Fine Arts", "subjects": []},
        "L": {"name": "Language Arts", "subjects": []},
        "M": {"name": "Math", "subjects": []},
        "ML": {"name": "Modern Language", "subjects": []},
        "SC": {"name": "Science", "subjects": []},
        "SS": {"name": "Social Studies", "subjects": []},
        "V": {"name": "Vocational Arts Courses", "subjects": []},
        "W": {"name": "Wellness/Health/PE", "subjects": []},
        "E": {"name": "Elementary", "subjects": []},
        "MT": {"name": "Mentorship", "subjects": []},
    }
    subjects = Subject.objects.all().order_by('category', 'name')
    for subject in subjects:
        subject_categories[subject.category]["subjects"].append(subject)

    position_categories = {
        'A': {"name": 'Administrative', "positions": []},
        'T': {"name": 'Teaching', "positions": []},
        'G': {"name": 'General_Staff', "positions": []},
    }
    positions = StaffPosition.objects.all().order_by('category', 'name')
    for position in positions:
        position_categories[position.category]["positions"].append(position)

    if personnelID:
        personnel_instance = get_object_or_404(Personnel, id=personnelID)
    else:
        personnel_instance = Personnel()


    if request.method == 'POST':

        p_form = PersonnelForm(request.POST, instance=personnel_instance, schoolID=school)
        pd_formset = PersonnelDegreeFormset(request.POST, instance=personnel_instance, prefix='pd_formset')

        if 'delete' in request.POST:
            personnel_instance.delete()
            return redirect('employee_report', arID=arID)

        if p_form.is_valid() and pd_formset.is_valid():

            personnel = p_form.save(commit=False)
            personnel.annual_report_id = arID

            try:
                with transaction.atomic():
                    personnel.save()
                    p_form.save_m2m()

                    subjects_teaching = p_form.cleaned_data.get('subjects_teaching')
                    subjects_taught = p_form.cleaned_data.get('subjects_taught')
                    if subjects_teaching:
                        subjects_taught_ids = set(subjects_taught.values_list('id', flat=True))
                        subjects_teaching_ids = set(subjects_teaching.values_list('id', flat=True))
                        all_subject_ids = list(subjects_taught_ids | subjects_teaching_ids)
                        personnel.subjects_taught.set(all_subject_ids)

                    pd_formset.save()

                if 'submit' in request.POST:
                    return redirect('employee_report', arID=arID)
                else:
                    return redirect('employee_add', arID=arID, positionCode=positionCode)


            except IntegrityError:
                p_form.add_error(None, "Personnel with this name already exists in this report.")

        else:
            print("Form errors:", p_form.errors)
            print("Formset errors:", pd_formset.errors)

    else:
        p_form = PersonnelForm(instance=personnel_instance, schoolID=school)
        pd_formset = PersonnelDegreeFormset(instance=personnel_instance, prefix='pd_formset')

    context = {
        'p_form': p_form,
        'pd_formset': pd_formset,
        'subject_categories': subject_categories,
        'position_categories': position_categories,
        'positionCode': positionCode,
        'arID':arID,
    }

    return render(request, 'employee_add_edit.html', context)

@login_required(login_url='login')
def import_employee_prev_year(request, arID):

    report = get_object_or_404(AnnualReport, id=arID)
    prev_school_year = report.school_year.get_previous_school_year()

    if not prev_school_year:
        messages.error(request, 'No previous school year found.')
        return redirect('employee_report' , arID)  # Update this with where you want to redirect

    prev_report = AnnualReport.objects.filter(school=report.school, school_year=prev_school_year,
                                              report_type=report.report_type).first()

    if not prev_report:
        messages.error(request, 'No previous report found.')
        return redirect('student_report', arID)  # Update this with where you want to redirect

    employee_to_import = Personnel.objects.filter(annual_report=prev_report).exclude(status=StaffStatus.NO_LONGER_EMPLOYED)


    # Now copy over all staff
    imported_count = 0
    not_imported_people = []
    for e in employee_to_import:

        old_positions = e.positions.all()
        old_degrees = PersonnelDegree.objects.filter(personnel=e)
        old_subjects_teaching = e.subjects_teaching.all()
        old_subjects_taught = e.subjects_taught.all()

        if Personnel.objects.filter(last_name=e.last_name, first_name=e.first_name, annual_report=report).exists():
            not_imported_people.append(f'{e.first_name} {e.last_name}')
            continue

        e.pk = None  # Makes Django create a new instance
        e.annual_report = report
        e.save()
        e.positions.set(old_positions)

        if e.years_administrative_experience is None:
            e.years_administrative_experience = 0


        if e.positions.filter(category='A').exists():
            if e.years_administrative_experience is None:
                e.years_administrative_experience = 1
            else:
                e.years_administrative_experience +=1
        if e.positions.filter(category='T').exists():
            if e.years_teaching_experience is None:
                e.years_teaching_experience = 1
            else:
                e.years_teaching_experience +=1
        if e.positions.filter(category='G').exists():
            if e.years_work_experience is None:
                e.years_work_experience = 1
            else:
                e.years_work_experience += 1

        if e.years_at_this_school:
            e.years_at_this_school += 1

        e.save()

        for d in old_degrees:
            PersonnelDegree.objects.create(
                personnel=e,
                degree=d.degree,
                area_of_study=d.area_of_study
            )
        e.subjects_teaching.set(old_subjects_teaching)
        e.subjects_taught.set(old_subjects_taught)

        imported_count += 1  # increment the count of imported students

    if imported_count > 0:
        messages.success(request, '{} Employees imported successfully.'.format(imported_count))
    if not_imported_people:
        messages.info(request, f'These employees were already entered in the report: {", ".join(not_imported_people)}')

    return redirect('employee_report', arID)  # Update this with where you want to redirect after successLEt me

#@login_required(login_url='login')
#def employee_report_display(request, arID):
#    return render(request, 'employee_report_display.html')

@login_required
def get_teacher_email(request):
    # Get the teacher id from the request
    teacher_id = request.GET.get('teacher_id', None)
    if teacher_id is not None:
        # Fetch the teacher instance and its related user's email
        try:
            teacher = Teacher.objects.select_related('user').get(id=teacher_id)
            email = teacher.user.email
            phone_number = teacher.phone_number
        except Teacher.DoesNotExist:
            return JsonResponse({"error": "Teacher not found"}, status=404)

        # Return the fetched email as a JsonResponse
        print(phone_number)
        return JsonResponse({"email": email, "phone_number": phone_number})

    # Return an error if no teacher id is provided in the request
    return JsonResponse({"error": "No teacher id provided"}, status=400)


@login_required(login_url='login')
def inservice_report(request, arID):
    annual_report=AnnualReport.objects.get(id=arID)
    schoolID=annual_report.school.id
    school_yearID=annual_report.school_year.id

    try:
        report_type_190_day = ReportType.objects.get(name='190 - Day Report')

        day190report = AnnualReport.objects.get(school_id=schoolID,school_year_id=school_yearID,
            report_type=report_type_190_day
        )
        day190_instance = day190report.day190.first()

        if day190_instance:  # Check if Day190 instance exists
            planed_inservices = day190_instance.inservice_discretionary_days.exclude(type='DS')
            planed_hours = sum(inservice.hours for inservice in planed_inservices)
        else:
            planed_inservices = None
            planed_hours = None
    except ObjectDoesNotExist:
        planed_inservices = None
        planed_hours = None


    InserviceFormset = modelformset_factory(Inservice, form=InserviceForm, extra=3, can_delete=True)

    inservices = Inservice.objects.filter(annual_report=annual_report)

    if request.method == 'POST':
        formset = InserviceFormset(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                if form.has_changed():
                    instance = form.save(commit=False)
                    instance.annual_report = annual_report
                    instance.save()
            formset.save()

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', schoolID)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', schoolID)
            else:
                return redirect('inservice_report', arID=arID)
        else:
            for form in formset:
                print(form.errors)

    else:
        formset = InserviceFormset(queryset=inservices)

    total_hours = sum(inservice.hours for inservice in inservices)

    context = {
        'annual_report': annual_report,
        'inservices': inservices,
        'formset':formset,
        'schoolID':schoolID,
        'total_hours':total_hours,
        'planed_inservices':planed_inservices,
        'planed_hours':planed_hours
    }
    return render(request, 'inservice_report.html', context)

@login_required(login_url='login')
def inservice_report_display(request, arID):

    annual_report=AnnualReport.objects.get(id=arID)
    inservices = Inservice.objects.filter(annual_report = annual_report)

    total_hours = inservices.aggregate(Sum('hours'))['hours__sum']
    if total_hours is None:
        total_hours = 0
    if total_hours < 30:
        enough=False
    else:
        enough=True

    context ={'inservices':inservices, 'total_hours':total_hours, 'enough':enough, 'arID':arID, 'annual_report':annual_report}

    return render(request, 'inservice_report_display.html', context)


@login_required(login_url='login')
def opening_report(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)

    if request.method == 'POST':
        if not annual_report.submit_date:
            annual_report.submit_date = date.today()
        annual_report.last_update_date = date.today()
        annual_report.save()
        return redirect('school_dashboard', annual_report.school.id)

    annual_report_student = AnnualReport.objects.get(report_type__code='SR', school= annual_report.school, school_year= annual_report.school_year)
    arStudentID = annual_report_student.id
    annual_report_personnel = AnnualReport.objects.get(report_type__code='ER', school= annual_report.school, school_year= annual_report.school_year)
    arEmployeeID = annual_report_personnel.id

    part_time_grade_count_fields=None
    grade_count_fields=None

    with transaction.atomic():
        opening, created = Opening.objects.get_or_create(annual_report=annual_report)

        part_time_students = Student.objects.filter(annual_report=annual_report_student, status="part-time", registration_date__lt=annual_report_student.submit_date)
        if part_time_students.exists():
            part_time_grade_counts = {'grade_{}_count'.format(i): part_time_students.filter(grade_level=i).count() for i in range(-2, 13)}
            part_time_grade_counts["pre_k_count"] = part_time_grade_counts.pop("grade_-2_count")
            part_time_grade_counts["k_count"] = part_time_grade_counts.pop("grade_-1_count")

            part_time_grade_count, created = PartTimeGradeCount.objects.update_or_create(
                opening=opening,
                defaults=part_time_grade_counts)

            #part_time_grade_count = PartTimeGradeCount.objects.create(**part_time_grade_counts)
            #opening.part_time_grade_count = part_time_grade_count

            part_time_grade_count_fields = [(field.verbose_name, getattr(part_time_grade_count, field.name)) for field in
                                  PartTimeGradeCount._meta.fields if field.name != 'id']



        students= Student.objects.filter(annual_report=annual_report_student, status="enrolled",  registration_date__lt=annual_report_student.submit_date)
        if not students.exists():
            students = Student.objects.filter(annual_report=annual_report_student, status="enrolled",
                                              registration_date__lt=annual_report_student.submit_date + timedelta(weeks=3))

        if students.exists():
            grade_counts = {'grade_{}_count'.format(i): students.filter(grade_level=i).count() for i in range(-2, 13)}
            grade_counts["pre_k_count"] = grade_counts.pop("grade_-2_count")
            grade_counts["k_count"] = grade_counts.pop("grade_-1_count")

            grade_count, created = GradeCount.objects.update_or_create(
                opening=opening,
                defaults=grade_counts)

            #grade_count = GradeCount.objects.create(**grade_counts)
            #opening.grade_count = grade_count

            grade_count_fields = [(field.verbose_name, getattr(grade_count, field.name)) for field in
                                  GradeCount._meta.fields if field.name != 'id']

            opening.girl_count = students.filter(gender="F").count()
            opening.boy_count = students.filter(gender="M").count()
            opening.graduated_count = Student.objects.filter(annual_report=annual_report_student, status="graduated").count()
            opening.did_not_return_count = Student.objects.filter(annual_report=annual_report_student, status="did_not_return").count()

            grade_ranges = {'K': range(-2, 0), 'E': range(0, 9), 'S': range(9, 13), }

            opening.boarding_girl_count_E = students.filter(gender="F", boarding=True, grade_level__in=grade_ranges['E']).count()
            opening.boarding_boy_count_E=students.filter(gender="M", boarding=True, grade_level__in=grade_ranges['E']).count()
            opening.boarding_girl_count_S = students.filter(gender="F", boarding=True, grade_level__in=grade_ranges['S']).count()
            opening.boarding_boy_count_S = students.filter(gender="M", boarding=True, grade_level__in=grade_ranges['S']).count()
            opening.day_girl_count_E = students.filter(gender="F", boarding=False, grade_level__in=grade_ranges['E']).count()
            opening.day_boy_count_E = students.filter(gender="M", boarding=False, grade_level__in=grade_ranges['E']).count()
            opening.day_girl_count_S = students.filter(gender="F", boarding=False, grade_level__in=grade_ranges['S']).count()
            opening.day_boy_count_S = students.filter(gender="M", boarding=False, grade_level__in=grade_ranges['S']).count()

#baptism counts

            conditions = {
                'baptized_parent_sda_count': ('Y', 'Y'),
                'baptized_parent_non_sda_count': ('Y', ['N','U']),
                'unbaptized_parent_sda_count': ('N', 'Y'),
                'unbaptized_parent_non_sda_count': ('N', ['N','U']),
            }

            for range_name, grade_range in grade_ranges.items():
                for count_name, (baptized, parent_sda) in conditions.items():
                    field_name = f"{count_name}_{range_name}"
                    count = students.filter(
                        baptized=baptized,
                        parent_sda__in=parent_sda,
                        grade_level__in=grade_range).count()
                    setattr(opening, field_name, count)

            unkown_baptismal_status_count = students.filter(baptized='U').count()

        personnel = Personnel.objects.filter(annual_report=annual_report_personnel).annotate(highest_degree_rank=Max('degrees__rank'))

        if personnel.exists():
            teacher_admin=personnel.filter(
                Q(positions__category=StaffCategory.ADMINISTRATIVE) |
                Q(positions__category=StaffCategory.TEACHING))
            opening.teacher_admin_count=teacher_admin.count()
            opening.general_staff_count=personnel.filter(positions__category=StaffCategory.GENERAL_STAFF).count()
            opening.non_sda_teacher_admin_count=teacher_admin.filter(sda=False).count()

            opening.professional_count = personnel.filter(highest_degree_rank=1).count()
            opening.doctorate_count = personnel.filter(highest_degree_rank=5).count()
            opening.masters_count = personnel.filter(highest_degree_rank=4).count()
            opening.bachelor_count = personnel.filter(highest_degree_rank=3).count()
            opening.associate_count = personnel.filter(highest_degree_rank=2).count()

        opening.save()

    context = dict(arStudentID= arStudentID, arEmployeeID=arEmployeeID,
                    opening=opening,
                   grade_count_fields=grade_count_fields, part_time_grade_count_fields=part_time_grade_count_fields,
                   unkown_baptismal_status_count=unkown_baptismal_status_count,
                   )


    return render(request, 'opening_report.html', context)

@login_required(login_url='login')
def opening_report_display(request, arID):
    annual_report = AnnualReport.objects.get(id=arID)
    if hasattr(annual_report, 'opening'):
        opening = annual_report.opening
        grade_count = opening.grade_count
        grade_count_fields = [(field.verbose_name, getattr(grade_count, field.name)) for field in
                              GradeCount._meta.fields if field.name != 'id']

        part_time_grade_count = opening.part_time_grade_count
        if part_time_grade_count:
            part_time_grade_count_fields = [(field.verbose_name, getattr(part_time_grade_count, field.name)) for field in PartTimeGradeCount._meta.fields if field.name != 'id']
        else:
            part_time_grade_count_fields = None
    else:
        opening = None
        grade_count_fields = None

    context = dict(opening=opening, grade_count_fields = grade_count_fields, part_time_grade_count_fields = part_time_grade_count_fields,
                   display=True )

    return render(request, 'opening_report.html', context)

@login_required(login_url='login')
def closing_report(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    closing, created = Closing.objects.get_or_create(annual_report=annual_report)

    if request.method == 'POST':
        form = ClosingForm(request.POST, instance=closing)
        if form.is_valid():
            form.save()

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', annual_report.school.id)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', annual_report.school.id)
            else:
                return redirect('closing_report', arID=arID)

    else:
        form = ClosingForm(instance=closing)


    annual_report_student = AnnualReport.objects.get(report_type__code='SR', school=annual_report.school,
                                                     school_year=annual_report.school_year)
    arStudentID = annual_report_student.id

    opening_report = AnnualReport.objects.filter(school_year=annual_report.school_year, school=annual_report.school,
                                                 report_type__code="OR").first()
    if opening_report:
        start_date = opening_report.submit_date
    else:
        start_date = None

    with transaction.atomic():
        students = Student.objects.filter(annual_report=annual_report_student,  status__in=['enrolled', 'part-time'])

        if students.exists():
            closing.withdraw_count = Student.objects.filter(annual_report=annual_report_student,
                                                            status="withdrawn").count()
            closing.new_student_count = students.filter(annual_report=annual_report_student,
                                                        registration_date__gt=start_date).count()

            full_time_students = Student.objects.filter(annual_report=annual_report_student, status='enrolled')
            grade_counts = {'grade_{}_count'.format(i): full_time_students.filter(grade_level=i).count() for i in range(-2, 13)}
            grade_counts["pre_k_count"] = grade_counts.pop("grade_-2_count")
            grade_counts["k_count"] = grade_counts.pop("grade_-1_count")

            grade_count, created = GradeCount.objects.update_or_create(
                closing=closing,
                defaults=grade_counts)
            grade_count_fields = [(field.verbose_name, getattr(grade_count, field.name)) for field in
                                  GradeCount._meta.fields if field.name != 'id']

            part_time_students = Student.objects.filter(annual_report=annual_report_student, status='part-time')
            if part_time_students.exists():
                part_time_grade_counts = {'grade_{}_count'.format(i): part_time_students.filter(grade_level=i).count() for i in
                                range(-2, 13)}
                part_time_grade_counts["pre_k_count"] = part_time_grade_counts.pop("grade_-2_count")
                part_time_grade_counts["k_count"] = part_time_grade_counts.pop("grade_-1_count")

                part_time_grade_count, created = PartTimeGradeCount.objects.update_or_create(
                    closing=closing,
                    defaults=part_time_grade_counts)
                part_time_grade_count_fields = [(field.verbose_name, getattr(part_time_grade_count, field.name)) for field in
                                  PartTimeGradeCount._meta.fields if field.name != 'id']
            else:
                part_time_grade_count_fields = None

    closing.save()
    context = dict(form=form, closing=closing, grade_count_fields = grade_count_fields,
                   part_time_grade_count_fields = part_time_grade_count_fields,
                   arStudentID=arStudentID)

    return render(request, 'closing_report.html', context)

@login_required(login_url='login')
def closing_report_display(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    if hasattr(annual_report, 'closing'):
        closing = annual_report.closing
        grade_count = closing.grade_count
        grade_count_fields = [(field.verbose_name, getattr(grade_count, field.name)) for field in
                              GradeCount._meta.fields if field.name != 'id']
        part_time_grade_count = closing.part_time_grade_count
        part_time_grade_count_fields = [(field.verbose_name, getattr(part_time_grade_count, field.name)) for field in
                              PartTimeGradeCount._meta.fields if field.name != 'id']

    else:
        closing = None
        grade_count_fields = None

    context = dict(closing=closing, grade_count_fields=grade_count_fields, part_time_grade_count_fields=part_time_grade_count_fields)
    return render(request, 'closing_report_display.html', context)

@login_required(login_url='login')
def worthy_student_scholarship(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    wss, created = WorthyStudentScholarship.objects.get_or_create(annual_report=annual_report)

    if request.method == 'POST':
        form = WorthyStudentScholarshipForm(request.POST, request.FILES or None, instance=wss)
        if form.is_valid():
            form.save()

            if 'submit' in request.POST:
                if not annual_report.submit_date:
                    annual_report.submit_date = date.today()
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', annual_report.school.id)
            elif 'save' in request.POST:
                annual_report.last_update_date = date.today()
                annual_report.save()
                return redirect('school_dashboard', annual_report.school.id)
            else:
                return redirect('worthy_student_scholarship', arID=arID)

    else:
        form = WorthyStudentScholarshipForm(instance=wss)


    opening_report = AnnualReport.objects.filter(school_year=annual_report.school_year, school=annual_report.school,
                                                 report_type__code="OR").first()
    opening=Opening.objects.get(annual_report=opening_report)
    wss.opening_enrollment = opening.grade_count.academy_count()
    closing_report = AnnualReport.objects.filter(school_year=annual_report.school_year, school=annual_report.school,
                                                 report_type__code="CR").first()
    closing=Closing.objects.get(annual_report=closing_report)
    wss.closing_enrollment = closing.grade_count.academy_count()

    wss.save()

    context = dict(form=form, wss=wss, opening_enrollment=wss.opening_enrollment, closing_enrollment=wss.closing_enrollment)

    return render(request, 'worthy_student_scholarship.html', context)

@login_required(login_url='login')
def worthy_student_scholarship_display(request, arID):
    annual_report = AnnualReport.objects.get(id=arID)
    wss=WorthyStudentScholarship.objects.get(annual_report=annual_report)

    context = dict(wss=wss)
    return render(request, 'worthy_student_scholarship_display.html', context)

@login_required(login_url='login')
def ap_report(request, arID):
    # Add your processing here
    return render(request, 'ap_report.html')

@login_required(login_url='login')
def ap_report_display(request, arID):
    # Add your processing here
    return render(request, 'ap_report_display.html')
    

# using reported data
@login_required(login_url='login')
def isei_reporting_dashboard(request):

    current_school_year = SchoolYear.objects.get(current_school_year=True)
    #student_reports = AnnualReport.objects.filter(school_year=current_school_year, report_type__code="SR")
    #day190_report = AnnualReport.objects.filter(school_year=current_school_year, report_type="190")
    #employee_report = AnnualReport.objects.filter(school_year=current_school_year, report_type="ER")
    #inservice_report = AnnualReport.objects.filter(school_year=current_school_year, report_type="IR")
    #opening_report = AnnualReport.objects.filter(school_year=current_school_year, report_type="OR")
    #ap_report= AnnualReport.objects.filter(school_year=current_school_year, report_type="APR")

    report_types = ReportType.objects.all()
    schools = School.objects.filter(member=True).exclude(name="ISEI")

    # Prefetch the AnnualReports for the selected school year for each school
    schools = schools.prefetch_related(
        Prefetch('annualreport_set', queryset=AnnualReport.objects.filter(school_year__id= current_school_year.id),
                 to_attr='annual_reports')
    )

    wss_schools = School.objects.filter(address__country__code='US').exclude(abbreviation__in=["AAA", "LBE", "AIS"])

    context = {'schools':schools, 'wss_schools':wss_schools, 'report_types':report_types, 'todays_date': date.today()}

    return render(request, 'isei_reporting_dashboard.html', context)


@login_required(login_url='login')
def isei_worthy_student_scholarship(request):

    current_school_year = SchoolYear.objects.get(current_school_year=True)

    annual_reports=AnnualReport.objects.filter(school_year=current_school_year, report_type__code="WS")

    wssr=WorthyStudentScholarship.objects.filter(annual_report__in=annual_reports)

    context=dict(wssr=wssr, current_school_year=current_school_year)
    return render(request, 'isei_worthy_student_scholarship.html', context)


@login_required(login_url='login')
def school_directory(request):
    schools = School.objects.filter(member=True).order_by('name')

    context = dict(schools=schools)

    return render(request, 'school_directory.html', context)
