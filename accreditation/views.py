from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from django.contrib import messages

from .models import Accreditation
from .forms import *

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_accreditation_dashboard(request):

    #current_accreditations = Accreditation.objects.filter(status = Accreditation.AccreditationStatus.CURRENT ).order_by('school__name')
    #in_works_accreditations = Accreditation.objects.filter(status = Accreditation.AccreditationStatus.IN_WORKS ).order_by('school__name')
    #context=dict(current_accreditations=current_accreditations, in_works_accreditations=in_works_accreditations)

    accreditation_groups = {
        "in works": Accreditation.objects.filter(
            status=Accreditation.AccreditationStatus.IN_WORKS
        ).order_by('school__name'),
        "current": Accreditation.objects.filter(
            status=Accreditation.AccreditationStatus.CURRENT
        ).order_by('school__name'),
    }

    context = {
        'accreditation_groups': accreditation_groups,
    }
    return render(request, 'accreditation/isei_accreditation_dashboard.html', context)

def add_accreditation(request):
    if request.method == 'POST':
        form = AccreditationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('isei_accreditation_dashboard')
    else:
        form = AccreditationForm()

    context = {'form': form, 'add':True}
    return render(request, 'accreditation/manage_accreditation.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def edit_accreditation(request, id):
    accreditation = get_object_or_404(Accreditation, id=id)
    if request.method == 'POST':
        form = AccreditationForm(request.POST, instance=accreditation)
        if form.is_valid():
            form.save()
            #messages.success(request, "The accreditation has been updated!")
            return redirect('/isei_accreditation_dashboard/')
    else:
        form = AccreditationForm(instance=accreditation)
    context = {'form': form, 'edit':True}
    return render(request, 'accreditation/manage_accreditation.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def delete_accreditation(request, id):
    accreditation = get_object_or_404(Accreditation, id=id)
    if request.method == 'POST':
        accreditation.delete()
        #messages.success(request, "The accreditation has been deleted!")
        return redirect('/isei_accreditation_dashboard/')
    context = {'accreditation': accreditation}
    return render(request, 'accreditation/delete_accreditation.html', context)


