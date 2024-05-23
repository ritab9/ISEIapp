from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
                        #return redirect('principal_teachercert', user.id)
                        return redirect('principal_dashboard', user.teacher.school.id)
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
@allowed_users(allowed_roles=['principal', 'registrar'])
def principal_dashboard(request, schoolID):

    school=School.objects.get(id=schoolID)
    school_year=SchoolYear.objects.get(current_school_year=True)

    #school info section
    accreditation_info = AccreditationInfo.objects.filter(school=school, current_accreditation=True)

    # Teacher Certificates Section
    teachers = Teacher.objects.filter(school=school, user__is_active=True, user__groups__name__in=['teacher'])
    number_of_teachers = teachers.count()
    tcertificates = TCertificate.objects.filter(teacher__in=teachers, archived=False, renewal_date__gte=date.today())
    certified_teachers = teachers.filter(tcertificate__in=tcertificates).distinct()
    number_of_certified_teachers = certified_teachers.count()
    percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)

    # Get all ReportingDueDate objects for this region
    report_due_dates = ReportDueDate.objects.filter(region=school.address.country.region).order_by('report_type__order_number')
    annual_reports=[]
    for report_dd in report_due_dates:
        if report_dd.report_type.isei_created == False:
            annual_report, created = AnnualReport.objects.get_or_create(school=school, school_year=school_year,
                                              report_type=report_dd.report_type)
            annual_reports.append((annual_report, report_dd.get_actual_due_date()))
        else:
            try:
                annual_report, created = AnnualReport.objects.get(school=school,school_year=school_year,
                                                    report_type=report_dd.report_type)
                annual_reports.append((annual_report, report_dd.get_actual_due_date()))
            except AnnualReport.DoesNotExist:
                pass
    context = dict( percent_certified=percent_certified, number_of_teachers=number_of_teachers,
                    school = school, annual_reports = annual_reports,
                    accreditation_info=accreditation_info,
                  )

    return render(request, 'users/principal_dashboard.html', context)


#@login_required(login_url='login')
#@allowed_users(allowed_roles=['staff'])
#def transcript_status(request):
#    unprocessed_transcripts = CollegeAttended.objects.filter(teacher__user__is_active=True, transcript_processed= False)

#    context = dict(unprocessed_transcripts = unprocessed_transcripts)

#    return render(request, 'users/transcript_status.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_dashboard(request):

    schools=School.objects.filter(member=True).order_by('name')

    context = dict (schools=schools)
    return render(request, 'users/isei_dashboard.html', context)
