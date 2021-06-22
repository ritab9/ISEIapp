from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from .models import *
from .decorators import unauthenticated_user, allowed_users
from .filters import *
from .forms import *
from .utils import is_in_group


# authentication functions
@unauthenticated_user
def registerpage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
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

        if user is not None:
            login(request, user)
            if is_in_group(request.user, 'principal'):
                return redirect('principal_dashboard')
            else:
                if is_in_group(request.user, 'teacher'):
                    if user.date_joined.date() == user.last_login.date():
                        return redirect('account_settings')
                    else:
                        return redirect('teacher_dashboard')
                elif is_in_group(request.user, 'admin'):
                    return redirect('admin_dashboard')
                else:
                    messages.info(request, 'User not assigned to a group. Contact the site administrator!')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'users/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('login')

#set up only for teachers now
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def accountsettings(request):
    # TODO account settings for different categories of users
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        teacher_form = TeacherForm(request.POST, request.FILES or None, instance=request.user.teacher)
        if user_form.is_valid() and teacher_form.is_valid():
            user_form.save()
            teacher_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('account_settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        teacher_form = TeacherForm(instance=request.user.teacher)
    return render(request, 'users/account_settings.html', {
        'user_form': user_form,
        'teacher_form': teacher_form
    })


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admindashboard(request):
    #teachers = Teacher.objects.all()
    # TODO redo the dashboard, replace activity references
    #activities = PDAInstance.objects.all()

    #total_teachers = teachers.count()
    #total_activities = activities.count()


    #context = dict( teachers=teachers, activities=activities, total_teachers=total_teachers,
     #              total_activities=total_activities)
    return render(request, 'users/admin_dashboard.html', context=dict())

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def teacherdashboard(request):
    # TODO teacher dashboard
    teacher = request.user.teacher
    user_in = "teacher"
    context = dict(user_in=user_in,teacher=teacher)
    return render(request, 'users/teacher_dashboard.html', context)

