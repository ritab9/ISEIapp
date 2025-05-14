
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse

from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.urls import reverse

from django.forms import modelformset_factory
from django.db.models import Sum, Q, Count, Prefetch, Max, Case, When, Value, IntegerField
from .forms import *
from datetime import date, timedelta
from django.contrib import messages
from django.db import transaction, OperationalError

from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
import numpy as np

from django.http import FileResponse
from django.views import View
from django.views.generic import ListView
from io import BytesIO
from django.contrib.auth.decorators import login_required
from reporting.models import GRADE_LEVEL_DICT
from accreditation.models import Accreditation
from .filters import *

from users.models import OtherAgencyAccreditationInfo
from .functions import update_student_country_occurences
from teachercert.myfunctions import newest_certificate
from django.db import IntegrityError

from django.utils.dateparse import parse_date
from pandas import ExcelWriter



#individual school reports
@login_required(login_url='login')
def report_dashboard(request, schoolID, school_yearID):
    # Add your processing here
    return render(request, 'report_dashboard.html')

#Student Report Views
@login_required(login_url='login')
def student_report(request,arID):

    redirect_to_school_dashboard = False
    try:
        annual_report = AnnualReport.objects.select_related('school__street_address__country').get(id=arID)
        school = annual_report.school

        # Determine if the school is in US and in TN
        is_us_school = school.street_address.country.code == "US"
        is_tn_school = is_us_school and school.street_address.state_us == "TN"

        exclude_fields = ['annual_report', 'id', 'age_at_registration']
        if not is_us_school or not is_tn_school:
            exclude_fields.append('TN_county')

        if not is_us_school:
            exclude_fields.append('us_state')

        StudentFormSet = my_formset_factory(Student, form=StudentForm, extra=1, can_delete=True, exclude=exclude_fields,
                                              is_us_school=is_us_school, is_tn_school=is_tn_school, school=school)

        if request.method == 'POST':

            formset = StudentFormSet(request.POST, queryset=Student.objects.filter(annual_report=annual_report))
            all_forms_valid = True
            formset_instances = []


            for form in formset:

                if form.has_changed():

                    if 'registration_date' in form.data:
                        date_string = form.data['registration_date']
                        registration_date = parse_date(date_string)
                        if registration_date is None:
                            raise ValueError(f"Could not parse date: {date_string}")
                        form.data['registration_date'] = registration_date.isoformat()

                    if form.is_valid():

                        if form.instance.pk is not None:
                            form.save()
                        else:
                            instance=form.save(commit=False)
                            instance.annual_report = annual_report
                            formset_instances.append(instance)
                    else:
                        all_forms_valid = False


            if formset_instances:
                for instance in formset_instances:
                    if instance.birth_date and instance.registration_date:
                        instance.age_at_registration = instance.registration_date.year - instance.birth_date.year - (
                                (instance.registration_date.month, instance.registration_date.day) < (
                            instance.birth_date.month, instance.birth_date.day))
                    elif instance.age:
                        instance.age_at_registration = instance.age

                Student.objects.bulk_create(formset_instances)
                update_student_country_occurences(annual_report)


            for form in formset.deleted_forms:
                if form.instance.id:
                    form.instance.delete()

            if all_forms_valid:
                redirect_to_school_dashboard = True
                if 'submit' in request.POST:
                    if not annual_report.submit_date:
                        annual_report.submit_date = date.today()
                    annual_report.last_update_date = date.today()
                    annual_report.save()
                    #To do Send email to ISEI about it's completion
                    return redirect('school_dashboard', school.id)

                elif 'save' in request.POST:
                    annual_report.last_update_date = date.today()
                    annual_report.save()
                    #return redirect('school_dashboard', school.id)
                    return HttpResponsePermanentRedirect(reverse('school_dashboard', args=[school.id]))
            else:
                redirect_to_school_dashboard = False
                messages.error(request, 'Some forms are invalid. Please check your inputs.')

        else:
            redirect_to_school_dashboard = False
            status_order = Case(
                When(status='enrolled', then=Value(1)),
                When(status='part-time', then=Value(2)),
                When(status='withdrawn', then=Value(3)),
                When(status='graduated', then=Value(4)),
                When(status='did_not_return', then=Value(5)),
                default=Value(6),
                output_field=IntegerField()
            )

            if annual_report.submit_date:
                students_qs = (Student.objects.filter(annual_report=annual_report,  status__in=['enrolled', 'withdrawn', 'part-time'])
                               .select_related('country', 'TN_county')
                               .order_by(status_order,'grade_level', 'name'))
            else:
                students_qs = (Student.objects.filter(annual_report=annual_report)
                               .select_related('country', 'TN_county')
                               .order_by(status_order,'grade_level', 'name'))
            formset = StudentFormSet(queryset=students_qs)



    except AnnualReport.DoesNotExist:
        messages.error(request, f"AnnualReport with id {arID} doesn't exist.")
    except OperationalError as e:
        messages.error(request, f"Database connection error: {str(e)}. Please try again later.")
    except ValidationError as e:
        messages.error(request, f"Validation error: {str(e)}")
    except Exception as e:
        messages.error(request, f'An error occurred while processing your request: {str(e)}')
    finally:
        if redirect_to_school_dashboard == False:
            return render(request, 'student_report.html', {'formset': formset, 'annual_report': annual_report})
        else:
            return redirect('school_dashboard', school.id)

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
    status_order = Case(
        When(status='enrolled', then=Value(1)),
        When(status='part-time', then=Value(2)),
        When(status='withdrawn', then=Value(3)),
        When(status='graduated', then=Value(4)),
        When(status='did_not_return', then=Value(5)),
        default=Value(6),
        output_field=IntegerField()
    )
    students = Student.objects.filter(annual_report=annual_report).select_related('annual_report', 'country',
                                                                                 'TN_county').order_by(status_order,'grade_level', 'name')
    #students = Student.objects.filter(annual_report=annual_report, status__in=['enrolled','part-time','withdrawn']).select_related('annual_report', 'country',
                                                                                      #'TN_county').order_by('grade_level', 'name')

    #status = 'enrolled'
    filter_form = StudentFilterForm(request.GET or None, annual_report=annual_report)
    #initial = {'status': status}

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

    #students=students.filter(status=status)
    context = {
        'annual_report': annual_report,
        'students': students,
        'filter_form': filter_form,
    }
    return render(request, 'student_report_display.html', context)


class StudentExcelDownload(View):
    def get(self, request, *args, **kwargs):
        #TODO take out age; it's only for importing old data (or maybe keep it as an alternative to birth_date?)
        address = request.user.profile.school.street_address
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
    school_state = annual_report_instance.school.street_address.state_us

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
            updated_count = 0

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
                    annual_report=annual_report_instance,
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
                        'birth_date': birth_date,
                        'grade_level': grade_level,
                        'registration_date': registration_date,
                        'withdraw_date': withdraw_date,
                        'location': location,
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            if created_count > 0:
                messages.success(request,f"{created_count} student record(s) have been created.")
            elif updated_count > 0:
                messages.success(request, f"{updated_count} student record(s) have been updated.")
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
    address=school.street_address
    school_address = address.address_1
    school_city = address.city
    school_zip = address.zip_code
    school_state = address.state_us
    school_country = address.country
    school_phone= school.phone_number
    school_email = school.email
    school_principal = school.principal

    accreditations = OtherAgencyAccreditationInfo.objects.filter(school=school)

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
def employee_report(request, arID, show_all=False):
    #all_personnel = Personnel.objects.filter(annual_report__id=arID).exclude(status=StaffStatus.NO_LONGER_EMPLOYED).select_related('teacher', 'annual_report').prefetch_related(
    #    'positions', 'degrees', 'subjects_teaching', 'subjects_taught').order_by('last_name')
    if show_all:
        all_personnel = Personnel.objects.filter(annual_report__id=arID).select_related(
            'teacher', 'annual_report').prefetch_related(
            'positions', 'degrees', 'subjects_teaching', 'subjects_taught').order_by('last_name')
    else:
        all_personnel = Personnel.objects.filter(annual_report__id=arID).exclude(
            status=StaffStatus.NO_LONGER_EMPLOYED).select_related('teacher', 'annual_report').prefetch_related(
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


def calculate_grade_counts(students, allowed_grade_range):
    #grade_counts = {'grade_{}_count'.format(i): students.filter(grade_level=i).count() for i in allowed_grade_range}
    grade_counts = {'grade_{}_count'.format(i): students.filter(grade_level=i).count() for i in list(range(-2, 13)) + list(range(14, 17))}

    # Handle renaming of grades for Pre-K, K, GA-I, GA-II, GA-III
    if "grade_-2_count" in grade_counts: grade_counts["pre_k_count"] = grade_counts.pop("grade_-2_count")
    if "grade_-1_count" in grade_counts: grade_counts["k_count"] = grade_counts.pop("grade_-1_count")
    if "grade_14_count" in grade_counts: grade_counts["ga_i_count"] = grade_counts.pop("grade_14_count")
    if "grade_15_count" in grade_counts: grade_counts["ga_ii_count"] = grade_counts.pop("grade_15_count")
    if "grade_16_count" in grade_counts: grade_counts["ga_iii_count"] = grade_counts.pop("grade_16_count")

    return grade_counts

@login_required(login_url='login')
def opening_report(request, arID):

    annual_report = AnnualReport.objects.get(id=arID)
    opening, created = Opening.objects.get_or_create(annual_report=annual_report)
    school=annual_report.school

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

    allowed_grade_range = school.get_grade_range()
    part_time_grade_count_fields=None
    grade_count_fields=None

    with transaction.atomic():
        part_time_students = Student.objects.filter(annual_report=annual_report_student, status="part-time", registration_date__lte=annual_report_student.submit_date)
        if part_time_students.exists():
            part_time_grade_counts = calculate_grade_counts(part_time_students, allowed_grade_range)

            if opening.part_time_grade_count:
                # If part_time_grade_count exists, update it
                for key, value in part_time_grade_counts.items():
                    setattr(opening.part_time_grade_count, key, value)
                opening.part_time_grade_count.save()
            else:
                part_time_grade_count = PartTimeGradeCount.objects.create(**part_time_grade_counts)
                opening.part_time_grade_count = part_time_grade_count  # Associate the new part_time_grade_count with the opening
                opening.save()

            part_time_grade_count_fields = [(field.verbose_name, getattr(opening.part_time_grade_count, field.name)) for field in
                                  PartTimeGradeCount._meta.fields if field.name != 'id']

        students= Student.objects.filter(Q(status="enrolled") | Q(status="withdrawn"), annual_report=annual_report_student, registration_date__lte=annual_report_student.submit_date)
        if not students.exists():
            students = Student.objects.filter(Q(status="enrolled") | Q(status="withdrawn"), annual_report=annual_report_student,
                                              registration_date__lte=annual_report_student.submit_date + timedelta(weeks=3))

        if students.exists():
            grade_counts = calculate_grade_counts(students, school.get_grade_range())
            grade_count, created = GradeCount.objects.update_or_create(opening=opening, defaults=grade_counts)
            grade_count_fields = [(field.verbose_name, getattr(grade_count, field.name)) for field in
                                  GradeCount._meta.fields if field.name != 'id']

            opening.girl_count = students.filter(gender="F").count()
            opening.boy_count = students.filter(gender="M").count()
            opening.graduated_count = Student.objects.filter(annual_report=annual_report_student, status="graduated").count()
            opening.did_not_return_count = Student.objects.filter(annual_report=annual_report_student, status="did_not_return").count()

            grade_ranges = {'K': range(-2, 0), 'E': range(0, 9), 'S': range(9, 13), 'GA':range(14,17)}

            opening.boarding_girl_count_E = students.filter(gender="F", boarding=True, grade_level__in=grade_ranges['E']).count()
            opening.boarding_boy_count_E=students.filter(gender="M", boarding=True, grade_level__in=grade_ranges['E']).count()
            opening.boarding_girl_count_S = students.filter(gender="F", boarding=True, grade_level__in=grade_ranges['S']).count()
            opening.boarding_boy_count_S = students.filter(gender="M", boarding=True, grade_level__in=grade_ranges['S']).count()
            opening.day_girl_count_E = students.filter(gender="F", boarding=False, grade_level__in=grade_ranges['E']).count()
            opening.day_boy_count_E = students.filter(gender="M", boarding=False, grade_level__in=grade_ranges['E']).count()
            opening.day_girl_count_S = students.filter(gender="F", boarding=False, grade_level__in=grade_ranges['S']).count()
            opening.day_boy_count_S = students.filter(gender="M", boarding=False, grade_level__in=grade_ranges['S']).count()

            opening.boarding_girl_count_GA = students.filter(gender="F", boarding=True, grade_level__in=grade_ranges['GA']).count()
            opening.boarding_boy_count_GA = students.filter(gender="M", boarding=True, grade_level__in=grade_ranges['GA']).count()
            opening.day_girl_count_GA = students.filter(gender="F", boarding=False, grade_level__in=grade_ranges['GA']).count()
            opening.day_boy_count_GA = students.filter(gender="M", boarding=False, grade_level__in=grade_ranges['GA']).count()

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

            opening.unkown_baptismal_status_count = students.filter(baptized='U').count()
            opening.baptized_non_sda_count = students.filter(baptized='O').count()

        personnel = Personnel.objects.filter(annual_report=annual_report_personnel).annotate(highest_degree_rank=Max('degrees__rank'))

        if personnel.exists():
            teacher_admin=personnel.filter(
                Q(positions__category=StaffCategory.ADMINISTRATIVE) |
                Q(positions__category=StaffCategory.TEACHING))
            opening.teacher_admin_count=teacher_admin.count()

            general_staff = personnel.filter(positions__category=StaffCategory.GENERAL_STAFF).exclude(id__in=teacher_admin)
            opening.general_staff_count=general_staff.count()

            opening.non_sda_teacher_admin_count=teacher_admin.filter(sda=False).count()

            opening.professional_count = personnel.filter(highest_degree_rank=1).count()
            opening.doctorate_count = personnel.filter(highest_degree_rank=5).count()
            opening.masters_count = personnel.filter(highest_degree_rank=4).count()
            opening.bachelor_count = personnel.filter(highest_degree_rank=3).count()
            opening.associate_count = personnel.filter(highest_degree_rank=2).count()

        opening.save()



    context = dict(arStudentID= arStudentID, arEmployeeID=arEmployeeID, opening=opening,
                   grade_count_fields=grade_count_fields, part_time_grade_count_fields=part_time_grade_count_fields,
                   allowed_grade_range=allowed_grade_range,)

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
    school=annual_report.school
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

            grade_counts = calculate_grade_counts(full_time_students, school.get_grade_range())

             # Check if a GradeCount already exists for this closing
            if closing.grade_count:
                # If grade_count exists, update it
                for key, value in grade_counts.items():
                    setattr(closing.grade_count, key, value)
                closing.grade_count.save()
            else:
                # If grade_count does not exist, create a new one
                grade_count = GradeCount.objects.create(**grade_counts)
                closing.grade_count = grade_count  # Associate the new grade_count with the closing
                closing.save()

            # Access the grade count fields to store them in the closing report
            grade_count_fields = [
                (field.verbose_name, getattr(closing.grade_count, field.name))
                for field in GradeCount._meta.fields if field.name != 'id'
            ]

            part_time_students = Student.objects.filter(annual_report=annual_report_student, status='part-time')
            if part_time_students.exists():
                part_time_grade_counts = calculate_grade_counts(part_time_students, school.get_grade_range())

                # Check if a PartTimeGradeCount already exists for this closing
                if closing.part_time_grade_count:
                    # If part_time_grade_count exists, update it
                    for key, value in part_time_grade_counts.items():
                        setattr(closing.part_time_grade_count, key, value)
                    closing.part_time_grade_count.save()
                else:
                    # If part_time_grade_count does not exist, create a new one
                    part_time_grade_count = PartTimeGradeCount.objects.create(**part_time_grade_counts)
                    closing.part_time_grade_count = part_time_grade_count  # Associate the new part_time_grade_count with the closing
                    closing.save()

                part_time_grade_count_fields = [(field.verbose_name, getattr(closing.part_time_grade_count, field.name)) for field in
                                  PartTimeGradeCount._meta.fields if field.name != 'id']
            else:
                part_time_grade_count_fields = None
        else:
            part_time_grade_count_fields = None
            grade_count_fields = None

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
        if part_time_grade_count:
            part_time_grade_count_fields = [(field.verbose_name, getattr(part_time_grade_count, field.name)) for field
                                            in PartTimeGradeCount._meta.fields if field.name != 'id']
        else:
            part_time_grade_count_fields = None
    else:
        closing = None
        grade_count_fields = None
        part_time_grade_count_fields = None

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

    report_types = ReportType.objects.all()
    schools = School.objects.filter(member=True, active = True)

    # Prefetch the AnnualReports for the selected school year for each school
    schools = schools.prefetch_related(
        Prefetch('annualreport_set', queryset=AnnualReport.objects.filter(school_year__id= current_school_year.id),
                 to_attr='annual_reports')
    )

    wss_schools = School.objects.filter(worthy_student_report_needed = True)
    opening_report_codes = ['SR', 'ER', '190', 'OR']
    closing_report_codes = ['IR', 'CR', 'WS']

    context = {'schools':schools, 'wss_schools':wss_schools, 'report_types':report_types, 'todays_date': date.today(),
               'opening_report_codes': opening_report_codes, 'closing_report_codes': closing_report_codes,
               'dashboard':True}

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
    schools = School.objects.filter(active=True).order_by('name')

    context = dict(schools=schools)

    return render(request, 'school_directory.html', context)

@login_required(login_url='login')
def download_TN_reports(request, schoolyearID):

    school_year=SchoolYear.objects.get(id=schoolyearID)

    annual_student_reports = AnnualReport.objects.filter(
        school_year=school_year,
        report_type__code="SR",
        school__street_address__state_us='TN'
    )

    # Prepare data for DataFrame
    data = []
    for report in annual_student_reports:
        school = report.school
        annual_employee_reports = AnnualReport.objects.filter(
            school_year=school_year,
            report_type__code="ER",
            school=school,
        )
        teacher_count = 0
        for employee_report in annual_employee_reports:
            teacher_count += Personnel.objects.filter(
                annual_report=employee_report,
                positions__teaching_position=True,
                status__in=[StaffStatus.FULL_TIME, StaffStatus.PART_TIME, StaffStatus.VOLUNTEER]
            ).distinct().count()

        student_count = report.students.filter(status="enrolled").count()
        data.append({
            'School name': school.name,
            'Address': school.street_address.address_1,
            'City': school.street_address.city,
            'Zip code': school.street_address.zip_code,
            'TN County': school.street_address.tn_county,
            'Principal': school.principal,
            'Email': school.email,
            'Phone number': school.phone_number,
            'School website': school.website,
            'Date of last Fire marshal': str(school.fire_marshal_date) if school.fire_marshal_date else None,
            'Enrollment': student_count,
            '# Teachers': teacher_count,
            'Grade Span': school.grade_levels,
        })

    df = pd.DataFrame(data)

    # Prepare Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=Annual_Reports_SR_{school_year.name}.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        # Write the school data to excel file
        df.to_excel(writer, index=False, sheet_name='Schools')

        # For storing school and counties
        county_records = {}

        # Now let's fetch Student data for all the TN schools and write it to a new sheet
        for report in annual_student_reports:
            school = report.school

            student_data = []
            students = Student.objects.filter(annual_report=report, us_state='TN', status='enrolled').exclude(grade_level=-2).order_by('TN_county')

            for student in students:
                student_data.append({
                    'Student Name': student.name,
                    'Age': student.age_at_registration,
                    'Address': student.address,
                    'TN County': student.TN_county.name if student.TN_county else None,
                })

            df_students = pd.DataFrame(student_data)
            df_students.to_excel(writer, index=False,
                                 sheet_name=f'{school.name[:28]}')  # Shortened school name to avoid Excel tab name length limit

            school_counties = students.values('TN_county').distinct()
            school_counties_list = [TNCounty.objects.get(id=county['TN_county']).name for county in school_counties
                                    if county['TN_county'] is not None]

            # Create a DataFrame for counties of the current school
            county_df = pd.DataFrame(school_counties_list, columns=[school.name])
            county_records[school.name] = county_df

        # Concatenate all the dataframes, pre-padding county lists of shorter length schools with null
        final_df = pd.concat(county_records.values(), ignore_index=True, axis=1)
        final_df.columns = county_records.keys()
        final_df.to_excel(writer, index=False, sheet_name='School and Counties')

    return response

@login_required(login_url='login')
def download_NCPSA_directory(request, schoolyearID):

    school_year=SchoolYear.objects.get(id=schoolyearID)

    annual_opening_reports = AnnualReport.objects.filter(
        school_year=school_year,
        report_type__code="OR",
    )

    # Prepare data for DataFrame
    data = []
    for report in annual_opening_reports:
        school = report.school

        try:
            enrollment = report.opening.opening_enrollment
        except Opening.DoesNotExist:
            enrollment = None

        #current_accreditation_info = OtherAgencyAccreditationInfo.objects.filter(school=school, current_accreditation=True).first()
        current_accreditation_info= Accreditation.objects.filter(school=school,status=Accreditation.AccreditationStatus.ACTIVE).first()

        if current_accreditation_info:
            accreditation_status = "Accredited"
            accreditation_end_date = current_accreditation_info.term_end_date.strftime(
                '%m/%d/%Y') if current_accreditation_info.term_end_date else None
            initial_accreditation_date = school.initial_accreditation_date.strftime(
                '%m/%d/%Y') if school.initial_accreditation_date else None
        else:
            accreditation_status = "Candidate"
            accreditation_end_date = None
            initial_accreditation_date = None

        if school.abbreviation == "AIS":
            representative = school.president + ",Director"
        else:
            representative = school.principal + ", Principal"

        data.append({
            'Institution': school.name,
            'Representative': representative,
            'Address': school.street_address.address_1,
            'City': school.street_address.city,
            'Zip code': school.street_address.zip_code,
            'State': school.street_address.state_us,
            'Country':school.street_address.country,
            'Phone': school.phone_number,
            'E-mail': school.email,
            'Website': school.website,
            'Public/Private': "Private",
            'Grades': school.grade_levels,
            'Enrollment': enrollment,
            'Accreditation Status':accreditation_status,
            'Initial Accreditation Date': initial_accreditation_date,
            'Accreditation Expiration Date': accreditation_end_date,
        })

    df = pd.DataFrame(data)

    # Prepare Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=Annual_Reports_SR_{school_year.name}.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        # Write the school data to excel file
        df.to_excel(writer, index=False, sheet_name='Schools')

    return response

class PersonnelListView(ListView):
    model = Personnel
    template_name = 'personnel_directory.html'  # change this to your desired template name
    filter_form=EmployeeFilterForm

    def get_form(self):
        if not self.request.GET:
            data = {'status': 'Active', 'position': 'Manager'}  # Default filter values
            school=self.kwargs.get('school')
            if school:
                data.update({'school': school})
            form=self.filter_form(data)
        else:
            form = self.filter_form(self.request.GET)
        return form

    def get_queryset(self):
        school=None
        school_id = self.kwargs.get('schoolID')  # assuming school year is passed via URL
        if school_id:
            school = School.objects.get(id=school_id)

        school_year = SchoolYear.objects.get(current_school_year=True)
        report_type = ReportType.objects.get(code="ER")

        form = self.filter_form(self.request.GET)
        if form.is_valid():
            if not school:
                school = form.cleaned_data.get('school')

            annual_employee_reports = AnnualReport.objects.filter(school_year=school_year,report_type=report_type, school=school)
            queryset = Personnel.objects.filter(annual_report__in=annual_employee_reports).order_by('annual_report','last_name')

            last_name = form.cleaned_data.get('last_name')
            status = form.cleaned_data.get('status')
            position = form.cleaned_data.get('position')
            degree = form.cleaned_data.get('degree')
            subjects_teaching = form.cleaned_data.get('subjects_teaching')

            if last_name:
                queryset = queryset.filter(last_name__icontains=last_name)
            if status and status != '':
                queryset = queryset.filter(status=status)
            if position:
                queryset = queryset.filter(positions=position)
            if degree:
                queryset = queryset.filter(degrees=degree)
            if subjects_teaching:
                queryset = queryset.filter(subjects_teaching=subjects_teaching)
        else:
            annual_employee_reports = AnnualReport.objects.filter(school_year=school_year, report_type=report_type,
                                                                  school=school)
            queryset = Personnel.objects.filter(annual_report__in=annual_employee_reports).order_by('annual_report',
                                                                                                    'last_name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.filter_form(self.request.GET)
        school_id = self.kwargs.get('schoolID')
        context['disable_school_select'] = bool(school_id)
        return context


@login_required(login_url='login')
def school_personnel_directory(request):
    filter_form=PersonnelFilterForm(request.GET)

    schools = School.objects.filter(active=True).exclude(Q(name="Sample School"))
    school_year = SchoolYear.objects.get(current_school_year=True)
    report_type = ReportType.objects.get(code="ER")

    if filter_form.is_valid() and filter_form.cleaned_data['school']:
            schools = schools.filter(name=filter_form.cleaned_data['school'])

    personnel_list = []

    for school in schools:
        try:
            annual_employee_report = AnnualReport.objects.get(school_year=school_year, report_type=report_type, school=school)
        except AnnualReport.DoesNotExist:
            continue

        staff = Personnel.objects.filter(annual_report=annual_employee_report).exclude(status="NE").order_by('last_name')
        if filter_form.cleaned_data.get('position'):
            staff = staff.filter(positions__name=filter_form.cleaned_data['position'])
        if filter_form.cleaned_data.get('subject'):
            staff = staff.filter(subjects_teaching__name=filter_form.cleaned_data['subject'])
        if filter_form.cleaned_data['name']:
            staff = staff.filter(
                Q(first_name__icontains=filter_form.cleaned_data['name']) | Q(last_name__icontains=filter_form.cleaned_data['name']))

        if not staff.exists():
            continue

        personnel_data = {}
        personnel_data["school"] = school
        personnel_data["staff"] = [{
            "last_name": person.last_name,
            "first_name": person.first_name,
            "positions": [position.name for position in person.positions.all()],
            "subjects": [subject.name for subject in person.subjects_teaching.all()],
            "email_address": person.email_address,
            "phone_number":person.phone_number,
        } for person in staff]

        personnel_list.append(personnel_data)

    context = {
        "school_personnel": personnel_list, "filter_form": filter_form,
    }

    return render(request, 'school_personnel_directory.html', context)

@login_required(login_url='login')
def longitudinal_enrollment(request, individual_school_name=None):

    if not individual_school_name:
        schools = School.objects.filter(active=True).order_by("name")
        individual_school = None
    else:
        schools = School.objects.filter(active=True, name=individual_school_name)
        individual_school = schools.first()

    if request.method == "POST":
        school_years = SchoolYear.objects.all()

        for school_year in school_years:
            for school in schools:
                allowed_grades = school.get_grade_range()
                annual_report = AnnualReport.objects.filter(school_year=school_year, school=school,
                                             report_type=ReportType.objects.get(code="SR")).first()
                if annual_report:
                    student_counts = (annual_report.students.filter(grade_level__in=allowed_grades)
                                      .values("grade_level").annotate(count=Count("id")))
                    # Create or update EnrollmentRecord for each grade level
                    for entry in student_counts:
                        grade = entry["grade_level"]
                        count = entry["count"]

                        LongitudinalEnrollment.objects.update_or_create(school=school,year=school_year,grade=grade,
                            defaults={"enrollment_count": count},)

    # Fetch enrollment data for display
    if not individual_school_name:
        records = LongitudinalEnrollment.objects.select_related("school", "year")
        grade_range = list(range(1, 13)) + [14, 15, 16]
    else:
        records =LongitudinalEnrollment.objects.filter(school__name=individual_school_name).select_related("school", "year")
        grade_range=individual_school.get_grade_range()


    enrollment_data_dict = {}

    for record in records:
        school_name = record.school.name
        year_name = record.year.name
        grade = record.grade
        enrollment_count = record.enrollment_count

        # Ensure the key (school_name) exists in the dictionary
        if school_name not in enrollment_data_dict:
            enrollment_data_dict[school_name] = {}

        # Ensure each year within the school has a dictionary of grade counts (1-12)
        if year_name not in enrollment_data_dict[school_name]:
            # Initialize counts for all grades (1-12) as 0
            enrollment_data_dict[school_name][year_name] = {grade: 0 for grade in grade_range}

        # Update the count for the specific grade for that school-year combination
        enrollment_data_dict[school_name][year_name][grade] = enrollment_count

        # Convert the dictionary to a list of dicts for template rendering
    enrollment_data = [
        {"school_name": school_name, "year_data": year_data}
        for school_name, year_data in sorted(enrollment_data_dict.items())  # Sort schools alphabetically
    ]

    for school in enrollment_data:
        for year_name, grade_counts in school["year_data"].items():
            total_enrollment = sum(grade_counts.values())
            school["year_data"][year_name]["total_enrollment"] = total_enrollment


    # Create the display labels from the choices
    # Create a mapping from value to label
    GRADE_LABELS = dict(Student.GRADE_LEVEL_CHOICES)
    grade_headers = [GRADE_LABELS[g] for g in grade_range]

    colors = ["dark-blue", "muted-orange", "muted-green",  "text-dark", "text-danger", "medium-blue",
              "text-success", "text-primary", "muted-orange", "muted-green", "text-dark", "text-danger"]

    context=dict(enrollment_data=enrollment_data, grade_range=grade_range, grade_headers=grade_headers, colors=colors,
                 individual_school_name=individual_school_name)
    return render(request, 'longitudinal_enrollment.html', context)


def add_enrollment(request, school_name=None, year_name=None):
    school = None
    year = None

    if school_name:
        school = get_object_or_404(School, name=school_name)
    if year_name:
        year = get_object_or_404(SchoolYear, name=year_name)

    if request.method == "POST":
        # If school and year not selected yet, pick from POST
        if not school or not year:
            school_name = request.POST.get('school')
            year_name = request.POST.get('year')
            if school_name and year_name:
                return redirect('add_enrollment_with_school_year', school_name=school_name, year_name=year_name)

        # If already have school and year, it's enrollment submission
        for grade in school.get_grade_range():
            enrollment_count = request.POST.get(f'enrollment_count_{grade}')
            if enrollment_count is not None:
                enrollment_count = int(enrollment_count or 0)
                enrollment_obj, created = LongitudinalEnrollment.objects.get_or_create(
                    school=school,
                    year=year,
                    grade=grade,
                    defaults={'enrollment_count': enrollment_count}
                )
                if not created:
                    enrollment_obj.enrollment_count = enrollment_count
                    enrollment_obj.save()

        next_url = request.GET.get('next') or reverse('longitudinal_enrollment_single', args=[school_name])
        return redirect(next_url)

    schools = School.objects.all().order_by('name')
    years = SchoolYear.objects.all().order_by('name')

    enrollment_data = {}
    if school and year:
        existing_enrollments = LongitudinalEnrollment.objects.filter(school=school, year=year)
        enrollment_data = {e.grade: e.enrollment_count for e in existing_enrollments}

        # Map grade numbers to their user-friendly labels
    grade_mapping = {v: k for k, v in GRADE_LEVEL_DICT.items()}

    context = {
        'school': school,
        'year': year,
        'schools': schools,
        'years': years,
        'enrollment_data': enrollment_data,
        'grade_mapping': grade_mapping
    }
    return render(request, 'add_enrollment.html', context)

