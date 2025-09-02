# annualvisits/views.py

from django.shortcuts import render, redirect
from django.forms import modelformset_factory

from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users

from services.models import Resource
#from users.models import School
#from teachercert.models import SchoolYear
from .forms import *
from .models import *



@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'principal', 'registrar'])
def school_annual_visit(request, school_id=None):

    current_year=SchoolYear.objects.filter(current_school_year=True).first()

    if school_id:
        school=School.objects.get(pk=school_id)
    else:
        school = request.user.profile.school

    documents = school.school_documents.first()
    #documents = SchoolDocument.objects.filter(school=school).first()

    documents_to_upload=Resource.objects.filter(name="Annual Visit Documentation").first()

    visits = AnnualVisit.objects.filter(school=school).order_by("-school_year__name", "-visit_date")

    context = dict(school=school, documents=documents, documents_to_upload=documents_to_upload, visits=visits, current_year=current_year)
    return render(request, "annualvisit/school_annual_visit.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_annual_visit(request):

    order_by = request.GET.get("order_by", "school__name")  # default sorting

    # validate to avoid SQL injection / bad field names
    allowed_fields = ["school__name", "visit_date", "representative"]
    if order_by not in allowed_fields:
        order_by = "school__name"

    current_year = SchoolYear.objects.filter(current_school_year=True).first()

    visits = AnnualVisit.objects.filter(school_year=current_year).select_related("school").order_by(order_by)

    for visit in visits:
        document = SchoolDocument.objects.filter(school=visit.school).first()
        visit.document_link = document.link if document else None

    context = dict(visits=visits, current_year=current_year)
    return render(request, "annualvisit/isei_annual_visit.html", context)


def manage_annual_visits(request):

    # 1. Get the current school year
    current_year = SchoolYear.objects.filter(current_school_year=True).first()

    if not current_year:
        return render(request, "annualvisit/manage_annual_visits.html", {"error": "No current school year set."})

    # 2. Ensure all active schools have an AnnualVisit
    active_schools = School.objects.filter(active=True).exclude(name__iexact="ISEI")
    for school in active_schools:
        AnnualVisit.objects.get_or_create(school=school, school_year=current_year)

    # 3. Create formset
    AnnualVisitFormSet = modelformset_factory(AnnualVisit, form=AnnualVisitForm, extra=0)
    queryset = AnnualVisit.objects.filter(school_year=current_year).select_related("school")

    if request.method == "POST":
        formset = AnnualVisitFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect("isei_annual_visit")
        else:
            print(formset.errors)
    else:
        formset = AnnualVisitFormSet(queryset=queryset)

    context = dict(formset=formset, current_year=current_year)
    return render(request, "annualvisit/manage_annual_visits.html", context)