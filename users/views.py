from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from datetime import timedelta

from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .utils import is_in_group
from .filters import *
from .myfunctions import *
from emailing.teacher_cert_functions import email_registered_user
from teachercert.models import Teacher, SchoolYear
from reporting.models import ReportDueDate, AnnualReport, ReportType
from users.models import School, Address
from django.http import HttpResponseRedirect
from services.models import TestOrder


# authentication functions
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def register_teacher(request):
    school = School.objects.all().order_by("name")
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
            teacher = Teacher.objects.create(user=new_user, first_name=new_user.first_name, last_name = new_user.last_name, school = school, joined_at=joined_at )
            username = form.cleaned_data.get('username')
            #phone_digits = request.POST['phone_dig']
            # flash message (only appears once)
            messages.success(request, 'Account was created for ' + username)

            email_registered_user(teacher)
            return redirect('account_settings', userID = new_user.id)

    context = {'form': form, 'school':school}
    return render(request, 'users/register_teacher.html', context)


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
                        #return redirect('principal_teachercert', user.teacher.school.id)
                        return redirect('school_dashboard', user.teacher.school.id)
                    elif is_in_group(request.user, 'teacher'):
                        return redirect('teacher_dashboard', user.id)
                    elif is_in_group(request.user, 'staff'):
                        #return redirect('isei_teachercert_dashboard')
                        return redirect('isei_dashboard')

                    else:
                        messages.info(request, 'User not assigned to a group. Please contact the site administrator.')
                else:
                    messages.info(request, 'This account is not currently active. Please contact ISEI.')
                    logout(request)
        else:
            messages.info(request, 'Username OR password is incorrect')
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
            school_of_employment_formset.save()
            messages.success(request, 'Your Schools of Employment List was successfully updated!')
        else:
            #messages.error(request, school_of_employment_formset.errors)
            employment_formset_valid = False
    else:
        school_of_employment_formset = SchoolOfEmploymentFormSet(instance=teacher)

    if request.method == 'POST' and request.POST.get('college_attended'):
        college_attended_formset = CollegeAttendedFormSet(request.POST, instance=teacher)
        if college_attended_formset.is_valid():
            college_attended_formset.save()
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

    school=School.objects.get(id=schoolID)
    school_year=school.current_school_year

    sr_report_type = ReportType.objects.get(code='SR')
    er_report_type = ReportType.objects.get(code='ER')
    or_submitted=AnnualReport.objects.filter(school=school, school_year=school_year,
                                    report_type__code="OR").exclude(submit_date__isnull=True).values_list('report_type__code', flat=True)

    submit_dates = AnnualReport.objects.filter(school=school, school_year=school_year,
                                    report_type__in=[sr_report_type, er_report_type]).exclude(
    submit_date__isnull=True).values_list('report_type__code', flat=True)
    if len(submit_dates) == 2:
        sr_er_submitted=True
    else:
        sr_er_submitted = False

    #school info section
    accreditation_info = AccreditationInfo.objects.filter(school=school, current_accreditation=True)

    # Teacher Certificates Section
    teachers = Teacher.objects.filter(school=school, user__is_active=True, user__groups__name__in=['teacher'])
    number_of_teachers = teachers.count()
    tcertificates = TCertificate.objects.filter(teacher__in=teachers, archived=False, renewal_date__gte=date.today())
    certified_teachers = teachers.filter(tcertificate__in=tcertificates).distinct()
    number_of_certified_teachers = certified_teachers.count()
    if number_of_teachers >0:
        percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)
    else:
        percent_certified = 0

    # Get all ReportingDueDate objects for this region
    report_due_dates = ReportDueDate.objects.filter(region=school.address.country.region).order_by('report_type__order_number')
    annual_reports=[]
    for report_dd in report_due_dates:
        # isei_created is false for APR (and possibly other reports in the future that need to be created specifically for each school by ISEI)
        if report_dd.report_type.isei_created == False:
            annual_report, created = AnnualReport.objects.get_or_create(school=school, school_year=school_year,
                                              report_type=report_dd.report_type)
            annual_reports.append((annual_report, report_dd.get_actual_due_date(school_year=school_year)))
        else:
            try:
                annual_report, created = AnnualReport.objects.get(school=school,school_year=school_year,
                                                    report_type=report_dd.report_type)
                annual_reports.append((annual_report, report_dd.get_actual_due_date(school_year=school_year)))
            except AnnualReport.DoesNotExist:
                pass

    test_orders = TestOrder.objects.filter(school=school)

    fire_marshal_date=school.fire_marshal_date
    if fire_marshal_date:
        one_year_ago = (timezone.now() - timezone.timedelta(days=365)).date()
        if fire_marshal_date <= one_year_ago:
            is_old=True
        else:
            is_old=False
    else:
        is_old=None


    context = dict( percent_certified=percent_certified, number_of_teachers=number_of_teachers,
                    school = school, annual_reports = annual_reports,
                    accreditation_info=accreditation_info,
                    sr_er_submitted = sr_er_submitted, or_submitted=or_submitted,
                    test_orders = test_orders,
                    is_old = is_old, fire_marshal_date=fire_marshal_date,
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

    return render(request, 'users/isei_dashboard.html')


def update_school_info(request, schoolID):

    school = get_object_or_404(School, id=schoolID)
    address = school.address

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
                try:
                    school = request.user.teacher.school
                    school.current_school_year = assigned_school_year
                    school.save()
                except AttributeError:
                    school_year_to_set_current = SchoolYear.objects.get(name=assigned_school_year)
                    school_year_to_set_current.current_school_year = True
                    school_year_to_set_current.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return HttpResponseRedirect('/')  # or any default redirect
