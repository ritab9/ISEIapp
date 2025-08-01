from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User

from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from datetime import timedelta
import random
import string

from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .utils import is_in_group
from .filters import *
from .myfunctions import *

from emailing.teacher_cert_functions import email_registered_user
from teachercert.models import Teacher, SchoolYear
from reporting.models import ReportDueDate, AnnualReport, ReportType
from users.models import School, Address, Teacher
from reporting.models import Personnel
from services.models import TestOrder
from accreditation.models import Accreditation
from apr.models import APR
from services.models import Resource

# authentication functions
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def register_teacher(request):
    school = School.objects.filter(active=True).order_by("name")
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            joined_at = request.POST['joined_at']
            school_id = request.POST['school_dropdown']
            group = Group.objects.get(name='teacher')
            new_user.groups.add(group)
            school=School.objects.get(id=school_id)
            teacher = Teacher.objects.create(user=new_user, first_name=new_user.first_name, last_name = new_user.last_name, joined_at=joined_at)
            username = form.cleaned_data.get('username')
            profile = UserProfile.objects.create(user=new_user, school=school)
            #phone_digits = request.POST['phone_dig']
            # flash message (only appears once)
            messages.success(request, 'Account was created for ' + username)

            email_registered_user(teacher)
            return redirect('account_settings', userID = new_user.id)

    context = {'form': form, 'school':school}
    return render(request, 'users/register_teacher.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'principal', 'registrar'])
def register_teacher_from_employee_report(request, personnelID):
    personnel = Personnel.objects.get(id=personnelID)
    school = personnel.annual_report.school

    username = f"{personnel.first_name}.{personnel.last_name}"

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        messages.error(request, "A user with this username already exists. Please contact ISEI.")
        return redirect('employee_report', personnel.annual_report.id)  # Replace with your actual redirect

    # Generate a random password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

    new_user = User.objects.create_user(
        username=username,
        password=password,
        email=personnel.email_address,
        first_name=personnel.first_name,
        last_name=personnel.last_name
    )
    group = Group.objects.get(name='teacher')
    new_user.groups.add(group)

    profile=UserProfile.objects.create(user=new_user, school=school)

    teacher = Teacher.objects.create(
        user=new_user,
        first_name=personnel.first_name,
        last_name=personnel.last_name,
        school=school,
        phone_number=personnel.phone_number,
        joined_at=timezone.now()  # make sure `joined_at` attribute is available in the `Personnel` model
    )
    personnel.teacher = teacher
    personnel.save()

    email_registered_user(teacher)

    messages.success(request, 'Account was created for ' + username)

    return redirect('employee_report', personnel.annual_report.id)

    #return redirect('personnel_directory', schoolID=school.id)

@unauthenticated_user
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                if request.user.is_active:
                    if is_in_group(request.user, 'principal') or is_in_group(request.user, 'registrar'):
                        return redirect('school_dashboard', user.profile.school.id)
                    elif is_in_group(request.user, 'teacher'):
                        return redirect('teacher_dashboard', user.id)
                    elif is_in_group(request.user, 'coordinating_team'):
                        return redirect('school_accreditation_dashboard', user.profile.school.id)
                    elif is_in_group(request.user, 'test_ordering'):
                        return redirect('test_order_dashboard', user.profile.school.id)
                    elif is_in_group(request.user, 'staff'):
                        return redirect('isei_dashboard')
                    elif is_in_group(request.user, 'scholarship_report'):
                        return redirect('worthy_student_scholarship_non_member', user.profile.school.id)
                    else:
                        messages.error(request, 'User not assigned to a group. Please contact ISEI.')
                        logout(request)
                        return redirect('login')  # Add this return statement
                else:
                    messages.error(request, 'This account is not currently active. Please contact ISEI.')
                    logout(request)
                    return redirect('login')  # Add this return statement
        else:
            messages.error(request, 'Username OR Password is incorrect. If you forgot your password click Reset Password above.'  )

    context = {}
    return render(request, 'users/login.html', context)



def logoutuser(request):
    logout(request)
    return redirect('login')


#set up only for teachers + principals now
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher','principal', 'registrar', 'staff'])
def accountsettings(request, userID):

    user = User.objects.get(id=userID)
    teacher = Teacher.objects.get(user=user)

    # checking if address already entered for user
    addresses = Address.objects.filter(teacher=teacher)
    address = addresses.first()
    if not address:
        address = Address(teacher=teacher)

    employment_formset_valid = True
    college_formset_valid = True
    teacher_form_valid = True
    address_form_valid= True

    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-end_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-end_date')

    if request.method == 'POST' and request.POST.get('teacher_info'):
        user_form = UserForm(request.POST, instance=user)
        teacher_form = TeacherForm(request.POST, request.FILES or None, instance=teacher)
        if user_form.is_valid() and teacher_form.is_valid():
            user_form.save()
            teacher_form.save()
            messages.success(request, 'Your profile was successfully updated!')
        else:
            #messages.error(request)
            teacher_form_valid = False

    else:
        user_form = UserForm(instance=user)
        teacher_form = TeacherForm(instance=teacher)

    if request.method == 'POST' and request.POST.get('address'):
        address_form = TeacherAddressForm(request.POST, instance=address)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.teacher = teacher
            address.save()
            messages.success(request, 'Your address was successfully updated!')
        else:
            #messages.error(request)
            address_form_valid = False
    else:
        # checking if address already entered for user
        addresses = Address.objects.filter(teacher=teacher)
        address = addresses.first()
        if address:
            address_form = TeacherAddressForm(instance=address)
        else:
            address_form = TeacherAddressForm(initial={'teacher': teacher})
            address = Address(teacher=teacher)

    if request.method == 'POST' and request.POST.get('school_of_employment'):
        school_of_employment_formset = SchoolOfEmploymentFormSet(request.POST, instance = teacher)
        if school_of_employment_formset.is_valid():
            instances = school_of_employment_formset.save(commit=False)
            for obj in school_of_employment_formset.deleted_objects:
                obj.delete()
            for instance in instances:
               instance.save()
            return redirect(request.path)
            messages.success(request, 'Your Schools of Employment List was successfully updated!')
        else:
            #messages.error(request, school_of_employment_formset.errors)
            employment_formset_valid = False
    else:
        school_of_employment_formset = SchoolOfEmploymentFormSet(instance=teacher)

    if request.method == 'POST' and request.POST.get('college_attended'):
        college_attended_formset = CollegeAttendedFormSet(request.POST, instance=teacher)
        if college_attended_formset.is_valid():
            instances = college_attended_formset.save(commit=False)
            for obj in college_attended_formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.save()
            return redirect(request.path)
            messages.success(request, 'Your Colleges Attended List was successfully updated!')
        else:
            #messages.error(request, college_attended_formset.errors)
            college_formset_valid = False
    else:
        college_attended_formset = CollegeAttendedFormSet(instance=teacher)


    #TODO This may not stay here. I will have to figure out the best way to
    #Initiate + Renew an application. Just convenient now for working purposes
    if TeacherCertificationApplication.objects.filter(teacher=teacher):
        application_submitted=True
    else:
        application_submitted = False



    context = dict(teacher=teacher, address = address, user = user, school_of_employment =school_of_employment, college_attended = college_attended,
                   teacher_form_valid = teacher_form_valid, address_form_valid = address_form_valid,
                   employment_formset_valid = employment_formset_valid, college_formset_valid = college_formset_valid,
                   user_form= user_form, teacher_form= teacher_form,
                   address_form = address_form,
                   application_submitted = application_submitted,
                   school_of_employment_formset = school_of_employment_formset,
                   college_attended_formset = college_attended_formset,
                   )

    return render(request, 'users/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar','staff'])
def school_dashboard(request, schoolID):
    #TODO Review this for efficiency. See what cases could benefit from prefertch related.

    school=School.objects.get(id=schoolID)
    school_year=school.current_school_year

    sr_report_type = ReportType.objects.get(code='SR')
    er_report_type = ReportType.objects.get(code='ER')
    or_submitted=AnnualReport.objects.filter(school=school, school_year=school_year,
                                    report_type__code="OR").exclude(submit_date__isnull=True).values_list('report_type__code', flat=True)
    cr_submitted = AnnualReport.objects.filter(school=school, school_year=school_year,
                                               report_type__code="CR").exclude(submit_date__isnull=True).values_list(
        'report_type__code', flat=True)

    submit_dates = AnnualReport.objects.filter(school=school, school_year=school_year,
                                    report_type__in=[sr_report_type, er_report_type]).exclude(
    submit_date__isnull=True).values_list('report_type__code', flat=True)
    if len(submit_dates) == 2:
        sr_er_submitted=True
    else:
        sr_er_submitted = False

    #school info section
    other_agency_accreditation_info = OtherAgencyAccreditationInfo.objects.filter(school=school, current_accreditation=True)

    # Teacher Certificates Section
    teachers = Teacher.objects.filter(user__profile__school=school, user__is_active=True, user__groups__name__in=['teacher'])
    number_of_teachers = teachers.count()
    tcertificates = TCertificate.objects.filter(teacher__in=teachers, archived=False, renewal_date__gte=date.today())
    certified_teachers = teachers.filter(tcertificate__in=tcertificates).distinct()
    number_of_certified_teachers = certified_teachers.count()
    if number_of_teachers >0:
        percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)
    else:
        percent_certified = 0

    #if school.street_address.country.code == "US" and school.abbreviation not in ["AAA", "LBE", "AIS"]:
    if school.worthy_student_report_needed:
        wss=True
    else:
        wss=False

    # Get all ReportingDueDate objects for this region
    # Get the region from the school's address
    region = school.street_address.country.region
     # Fetch all ReportDueDate objects for this region
    report_due_dates = ReportDueDate.objects.filter(region=region).order_by('report_type__order_number')

    annual_reports = []
    for report_due_date in report_due_dates:
        # Skip if report type is "WS" and wss is False
        if report_due_date.report_type.code == "WS" and not wss:
            continue

        # Get or create the annual report for the school and report type
        annual_report, _ = AnnualReport.objects.get_or_create(
            school=school,
            school_year=school_year,
            report_type=report_due_date.report_type
        )

        # Get the actual due date, considering the school
        due_date = report_due_date.get_actual_due_date(school=school, school_year=school_year)
        # Add to list
        annual_reports.append((annual_report, due_date))



    fire_marshal_date=school.fire_marshal_date
    if fire_marshal_date:
        one_year_ago = (timezone.now() - timezone.timedelta(days=365)).date()
        if fire_marshal_date <= one_year_ago:
            is_old=True
        else:
            is_old=False
    else:
        is_old=None

    accreditation = Accreditation.objects.filter(school=school, status = Accreditation.AccreditationStatus.ACTIVE).first()
    if accreditation:
        apr=APR.objects.filter(accreditation=accreditation).first()
    else:
        apr=None

    #Link to Safety and Maintenance Inspection Forms
    if school.street_address.country.code == "US":
        safety_form_link=Resource.objects.filter(name="Safety & Maintenance Inspection Form (USA)").values_list("link",flat=True).first()
    else:
        safety_form_link = Resource.objects.filter(name="Safety & Maintenance Inspection Form (International)").values_list("link",flat=True).first()

    context = dict( percent_certified=percent_certified, number_of_teachers=number_of_teachers,
                    school = school, annual_reports = annual_reports,
                    other_agency_accreditation_info=other_agency_accreditation_info, accreditation=accreditation,
                    sr_er_submitted = sr_er_submitted, or_submitted=or_submitted, cr_submitted=cr_submitted,
                    is_old = is_old, fire_marshal_date=fire_marshal_date, wss=wss,
                    apr=apr, dashboard=True,
                    safety_form_link=safety_form_link,
                  )

    return render(request, 'users/school_dashboard.html', context)


#@login_required(login_url='login')
#@allowed_users(allowed_roles=['staff'])
#def transcript_status(request):
#    unprocessed_transcripts = CollegeAttended.objects.filter(teacher__user__is_active=True, transcript_processed= False)

#    context = dict(unprocessed_transcripts = unprocessed_transcripts)

#    return render(request, 'users/transcript_status.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_dashboard(request):

    current_school_year = SchoolYear.objects.filter(current_school_year=True).first()

    context = dict(schoolyearID=current_school_year.id, dashboard=True)
    return render(request, 'users/isei_dashboard.html', context)


def update_school_info(request, schoolID):

    school = get_object_or_404(School, id=schoolID)
    address = school.street_address

    if address.state_us == "TN":
        tn_school=True
        fire_marshal_date = school.fire_marshal_date
        if fire_marshal_date:
            one_year_ago = (timezone.now() - timezone.timedelta(days=365)).date()
            if fire_marshal_date <= one_year_ago:
                is_old = True
            else:
                is_old = False
        else:
            is_old = True
    else:
        tn_school=False
        is_old=False

    if request.method == 'POST':
        form_school = SchoolForm(request.POST, instance=school)
        form_address = SchoolAddressForm(request.POST, instance=address)
        if form_school.is_valid() and form_address.is_valid():
            form_school.save()
            form_address.save()
            return redirect('school_dashboard', schoolID=schoolID)
    else:
        form_school = SchoolForm(instance=school)
        form_address = SchoolAddressForm(instance=address)



    context = {
        'form_school': form_school,
        'form_address': form_address,
        'schoolID':schoolID,
        'tn_school':tn_school, 'is_old':is_old,
    }

    return render(request, 'users/update_school_info.html', context)


def change_school_year(request):

    if request.method == 'POST':
        form = SchoolYearForm(request.POST)
        if form.is_valid():
            assigned_school_year = form.cleaned_data['school_year']

            if request.user.is_authenticated:
                if is_in_group(request.user, 'staff'):
                    school_year_to_set_current = SchoolYear.objects.get(name=assigned_school_year)
                    school_year_to_set_current.current_school_year = True
                    school_year_to_set_current.save()

                school = request.user.profile.school
                school.current_school_year = assigned_school_year
                school.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return HttpResponseRedirect('/')  # or any default redirect
