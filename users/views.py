from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
                return redirect('PDAreports')
                #return redirect('principal_dashboard')
            else:
                if is_in_group(request.user, 'teacher'):
                    #if user.date_joined.date() == user.last_login.date():
                    if certified(teacher):
                        return redirect('myPDAdashboard', user.id)
                    else:
                        #return redirect('teacher_dashboard') #because dashboard is not yet done
                        return redirect('account_settings', user.id)
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
    address = Address.objects.get(teacher=teacher)
    if not address:
        address = Address (initial={'teacher': teacher})

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
        address_form = TeacherAddressForm(request.POST)
        if address_form.is_valid():
            address_form.save()
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
def teacherdashboard(request):
    # TODO teacher dashboard
    teacher = request.user.teacher
    user_in = "teacher"

    # current_certificates
    tcertificate = TCertificate.objects.filter (teacher = teacher, archived= False)

    context = dict(user_in=user_in, teacher=teacher, tcertificate=tcertificate)
    return render(request, 'users/teacher_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal'])
def principaldashboard(request):
    principal = request.user.teacher
    teachers = Teacher.objects.filter(school=principal.school)
    context = dict(teachers=teachers, principal = principal)

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

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'principal'])
def teachercert_application(request, pk, appID = None):
# pk - teacher ID, appID - application ID

    teacher = Teacher.objects.get(id=pk)
    address = Address.objects.get(teacher=teacher)


    if request.method == 'POST':
        application_form = TeacherCertificationApplicationForm(request.POST)
        if application_form.is_valid():
            application_form.save()
            print("application")
    else:
        if appID==None: #new application
            application_form = TeacherCertificationApplicationForm(initial={'teacher': teacher})
        else: #update existing application
            application_form = TeacherCertificationApplicationForm(
                instance=TeacherCertificationApplication.objects.get(id=appID))


    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-start_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-start_date')

    context = dict(teacher = teacher, address = address,
                   application_form = application_form,
                   school_of_employment = school_of_employment, college_attended = college_attended,
                 )
    return render(request, 'users/teachercert_application.html', context)