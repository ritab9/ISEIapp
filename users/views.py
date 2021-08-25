from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from datetime import datetime, timedelta

from .decorators import unauthenticated_user, allowed_users
from .forms import *
from .utils import is_in_group
from .filters import *
from .models import *
from teachercert.models import *
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.forms import inlineformset_factory
# import custom functions
from .myfunctions import *
from teachercert.myfunctions import initial_application, last_application

# authentication functions
@unauthenticated_user
def registerpage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            # signal create_teacher is activated by post_save, User
            #TODO Should the action in signals.py be brought back here?
            username = form.cleaned_data.get('username')
            # flash message (only appears once)
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'users/register.html', context)


@unauthenticated_user
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        teacher = Teacher.objects.get(user=user)

        if user is not None:
            login(request, user)
            if is_in_group(request.user, 'principal'):
                #return redirect('principal_teachercert')
                #return redirect('PDAreports')
                return redirect('principal_dashboard')
            else:
                if is_in_group(request.user, 'teacher'):
                    #if user.date_joined.date() == user.last_login.date():
                    #if certified(teacher):
                    return redirect('teacher_dashboard', user.id)
                    #else:
                    #    return redirect('account_settings', user.id)
                elif is_in_group(request.user, 'staff'):
                    #return redirect('PDAreports')
                    return redirect('isei_teachercert')
                    #return redirect('staff_dashboard')
                else:
                    messages.info(request, 'User not assigned to a group. Contact the site administrator!')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'users/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('login')


#set up only for teachers + principals now
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher','principal'])
def accountsettings(request, userID):

    # TODO account settings for different categories of users
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
    if initial_application(teacher):
        application_submitted=True
        last_application_id = last_application(teacher).id
    else:
        application_submitted = False
        last_application_id = None

    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-start_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-start_date')


    context = dict(teacher=teacher, address = address, user = user, school_of_employment =school_of_employment, college_attended = college_attended,
                   teacher_form_valid = teacher_form_valid, address_form_valid = address_form_valid,
                   employment_formset_valid = employment_formset_valid, college_formset_valid = college_formset_valid,
                   user_form= user_form, teacher_form= teacher_form,
                   address_form = address_form,
                   application_submitted = application_submitted, last_application_id = last_application_id,
                   school_of_employment_formset = school_of_employment_formset,
                   college_attended_formset = college_attended_formset,
                   )

    return render(request, 'users/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', ])
def teacherdashboard(request, userID):
    # TODO teacher dashboard
    user=User.objects.get(id=userID)
    teacher = Teacher.objects.get(user = user)
    #user_in = "teacher"

    # current_certificates
    if certified(teacher):
        tcertificates = current_certificates(teacher)
    else:
        tcertificates = None

    #ToDo think on how to deal with teachers whose certification is not valid anymore (expired in longer than a year)
    # and need to reapply
    initial_app = initial_application(teacher)
    last_app = last_application(teacher)

    today =get_today()

    context = dict(teacher=teacher, tcertificates=tcertificates,
                   today=today, initial_app = initial_app,
                   last_app=last_app)
    return render(request, 'users/teacher_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal'])
def principaldashboard(request):
    principal = request.user.teacher

    teachers = Teacher.objects.filter(school=principal.school, active= True)

#Teacher Certificates Section
    number_of_teachers = teachers.count()
    tcertificates = TCertificate.objects.filter(teacher__school = principal.school, archived = False)

    #Valid certificates and certified teachers
    valid_tcertificates = tcertificates.filter(renewal_date__gte=date.today(), teacher__in = teachers).order_by('teacher')
    certified_teachers = teachers.filter(tcertificate__in = valid_tcertificates).distinct()
    number_of_certified_teachers = certified_teachers.count()

    #expired certificates and teachers with expired certificates
    expired_tcertificates = tcertificates.filter(renewal_date__lt = date.today()).order_by('teacher')
    expired_teachers = teachers.filter(tcertificate__in = expired_tcertificates)
    number_of_expired_teachers = expired_teachers.count()

    #not certified teachers
    non_certified_teachers = teachers.filter(~Q(tcertificate__in= tcertificates))
    number_of_non_certified_teachers = non_certified_teachers.count()

    percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)

    today = date.today()
    in_six_months = today + timedelta (183)
    a_year_ago = today - timedelta (365)

# Report Approval Section
    pda_report = PDAReport.objects.filter(teacher__school=principal.school)  # all the reports from this teacher's school
    pda_report_notreviewed = pda_report.filter(date_submitted__isnull=False, principal_reviewed='n')
    pda_instance_notreviewed = PDAInstance.objects.filter(pda_report__in=pda_report, pda_report__isei_reviewed='a', isei_reviewed='d', date_resubmitted__isnull=False, principal_reviewed='n')
    if pda_report_notreviewed or pda_instance_notreviewed:
        reports_to_review = True
    else:
        reports_to_review = False


    context = dict( today = today, in_six_months = in_six_months, a_year_ago=a_year_ago, percent_certified = percent_certified,
                   valid_tcertificates = valid_tcertificates, number_of_certified_teachers = number_of_certified_teachers,
                   expired_tcertificates = expired_tcertificates, number_of_expired_teachers = number_of_expired_teachers,
                  non_certified_teachers = non_certified_teachers, number_of_non_certified_teachers = number_of_non_certified_teachers,
                   number_of_teachers = number_of_teachers,
                    reports_to_review = reports_to_review)

    return render(request, 'users/principal_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def staffdashboard(request):
    # TODO redo the dashboard, replace activity references
    # teachers = Teacher.objects.all()
    # activities = PDAInstance.objects.all()
    # total_teachers = teachers.count()
    # total_activities = activities.count()
    # context = dict( teachers=teachers, activities=activities, total_teachers=total_teachers,
    #              total_activities=total_activities)
    return render(request, 'users/staff_dashboard.html', context=dict())
