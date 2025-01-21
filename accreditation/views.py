from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from selfstudy.models import SelfStudy
from users.decorators import allowed_users
from django.contrib import messages

from .models import Accreditation
from .forms import *

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_accreditation_dashboard(request):
    # Get sorting parameters from the request
    sort_by = request.GET.get('sort', 'school__name')  # Default sort field
    order = request.GET.get('order', 'asc')  # Default order is ascending

    ordering = sort_by if order == 'asc' else f'-{sort_by}' # Determine the ordering

    accreditation_groups = {
        "in works": Accreditation.objects.filter(
            status=Accreditation.AccreditationStatus.IN_WORKS
        ).order_by(ordering),
        "current": Accreditation.objects.filter(
            status=Accreditation.AccreditationStatus.CURRENT
        ).order_by(ordering),
    }

    context = {
        'accreditation_groups': accreditation_groups,
        'current_sort': sort_by,
        'current_order': order,
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

    context = {'form': form, 'add':True, }
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

    selfstudy=SelfStudy.objects.filter(accreditation=accreditation).first()

    context = {'form': form, 'edit':True, 'accreditation':accreditation, 'selfstudy':selfstudy}
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


