from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from selfstudy.models import SelfStudy
from users.decorators import allowed_users
from django.contrib import messages

from .models import Accreditation, Standard, InfoPage
from .forms import *
from users.models import SchoolType
from emailing.functions import send_simple_email

#ISEI Views
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_standards_indicators(request):
    standards = Standard.objects.top_level().prefetch_related('substandards', 'indicator_set')

    context=dict(standards=standards)
    return render(request, 'accreditation/isei_standards_indicators.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_accreditation_dashboard(request):
    # Get sorting parameters from the request
    sort_by = request.GET.get('sort', 'school__name')  # Default sort field
    order = request.GET.get('order', 'asc')  # Default order is ascending

    ordering = sort_by if order == 'asc' else f'-{sort_by}' # Determine the ordering

    accreditation_groups = {
        "scheduled": Accreditation.objects.filter(status=Accreditation.AccreditationStatus.SCHEDULED).order_by(ordering),
        "active": Accreditation.objects.filter(status=Accreditation.AccreditationStatus.ACTIVE).order_by(ordering),
         #"retired": Accreditation.objects.filter(status=Accreditation.AccreditationStatus.PAST).order_by(ordering),
    }

    now = timezone.now().date()
    months_ahead_6 = now + relativedelta(months=6)
    months_ahead_18 = now + relativedelta(months=19)

    context = dict(accreditation_groups=accreditation_groups,
                   current_sort_by=sort_by, current_order=order,
                   months_ahead_6=months_ahead_6, months_ahead_18=months_ahead_18)

    # Check if the "past" category was clicked
    if request.GET.get('category') == 'past':
        past_accreditations = Accreditation.objects.filter(status=Accreditation.AccreditationStatus.PAST).order_by(ordering)
        context['past_accreditations'] = past_accreditations
        context['include_past'] = True


    return render(request, 'accreditation/isei_accreditation_dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
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
            accreditation = form.save()  # Capture the saved instance
            school = accreditation.school

            # Set initial_accreditation_date if it doesn't exist and term_start_date is provided
            if not school.initial_accreditation_date and accreditation.term_start_date:
                school.initial_accreditation_date = accreditation.term_start_date
                school.save()

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


#School Accreditation Views

@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar', 'staff'])
def school_accreditation_dashboard(request, school_id):
    school=get_object_or_404(School, id=school_id)

    today = timezone.localdate()

    # 1️⃣ In‑progress = neither start nor end date set
    in_progress_app = AccreditationApplication.objects.filter(school=school,
        site_visit_start_date__isnull=True,site_visit_end_date__isnull=True).first()

    # 2️⃣ Scheduled = start date set, end date today or later
    upcoming_visit = AccreditationApplication.objects.filter( school=school,
        site_visit_start_date__isnull=False,site_visit_end_date__gte=today).order_by('-site_visit_start_date').first()

    # 3️⃣ Decide status and optional message
    if in_progress_app:
        application_status = "progress"
    elif upcoming_visit:
        application_status = "scheduled"
    else:
        application_status = "apply"

    #accreditation_scheduled = Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.SCHEDULED).first()
    #accreditation_active = Accreditation.objects.filter(status=Accreditation.AccreditationStatus.ACTIVE).first()
    #accreditation_past = Accreditation.objects.filter(status=Accreditation.AccreditationStatus.PAST)

    accreditation_groups = {
        "scheduled": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.SCHEDULED),
        "active": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.ACTIVE),
        "past": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.PAST),
    }

    context = dict(accreditation_groups =accreditation_groups, school=school,
                   application_status = application_status)

    return render(request, 'accreditation/school_accreditation_dashboard.html', context)

def map_school_type_choices_to_school_types(school, app):
    # Get the SchoolType objects to be used in SelfStudy
    #School selects it's type from a simple list (school_type_choice) but we need to
    #convert that list into a usable list to mark the SelfStudy Indicators
    all_types = SchoolType.objects.in_bulk(field_name='code')  # Assumes SchoolType has 'code' field like 'a', 'bm', etc.

    selected_codes = [choice.code for choice in school.school_type_choice.all()]
    result_codes = set()

    if 'v' in selected_codes:
        result_codes.add('v')  # Vocational stands alone
    else:
        result_codes.add('a')  # All non-vocational get 'a'

        if 'b' in selected_codes:
            result_codes.update(['bm', 'b'])

        if 'd' in selected_codes:
            result_codes.add('bm')

        if 'dl' in selected_codes:
            result_codes.add('dl')

        # Elementary school check (e.g. lowest grade < 7)
        if app.lowest_grade:
            if app.lowest_grade == "K" or app.lowest_grade == "PreK":
                grade = 0
            else: int(app.lowest_grade)

            if grade < 7:
                result_codes.add('e')

    # Map codes to SchoolType instances
    matching_school_types = [all_types[code] for code in result_codes if code in all_types]

    # Update the school's school_type field
    school.school_type.set(matching_school_types)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar', 'staff'])
def accreditation_application(request, school_id):
    school = get_object_or_404(School, id=school_id)
    info_page = InfoPage.objects.filter(slug="accreditation-application-intro").first()

    in_progress_app = AccreditationApplication.objects.filter(school=school,
                site_visit_start_date__isnull=True, site_visit_end_date__isnull=True).first()

    address_form = AddressForm(request.POST or None, instance=school.street_address, prefix="main", is_required=True)
    postal_address_form = AddressForm(request.POST or None, instance=school.postal_address, prefix="postal", is_required=False)

    school_form = SchoolInfoForApplicationForm(request.POST or None, instance=school)
    app_form = AccreditationApplicationForm(request.POST or None, instance= in_progress_app)

    if request.method == 'POST':
        if school_form.is_valid() and app_form.is_valid() and address_form.is_valid():
            school_form.save()
            address=address_form.save()
            school.street_address = address

            if postal_address_form.is_valid() and postal_address_form.has_changed() and postal_address_form.cleaned_data.get('country'):
                postal_address = postal_address_form.save()
                school.postal_address = postal_address

            school.save()

            app = app_form.save(commit=False)
            app.school = school
            app.save()
            map_school_type_choices_to_school_types(school,app)

            message=f"{school.name} has submitted an Accreditation Application"
            send_simple_email("Accreditation Application", message, ['info@iseiea.org'])

            messages.success(request, "Your application was submitted successfully.")
            return redirect('school_accreditation_dashboard', school_id=school_id)
        else:
            print("not valid")
            print("School form errors:", school_form.errors)
            print("Application form errors:", app_form.errors)
            print("Address form errors:", address_form.errors)
            print("Postal Address form errors:", postal_address_form.errors)

    context=dict(info_page=info_page, school=school,
                 app_form=app_form, school_form=school_form,
                 address_form = address_form, postal_address_form = postal_address_form)

    return render(request, 'accreditation/accreditation_application.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def accreditation_application_review(request, pk):
    info_page = InfoPage.objects.filter(slug="accreditation-application-intro").first()
    application = get_object_or_404(AccreditationApplication, pk=pk)
    school=application.school

    accreditation = Accreditation.objects.filter(school=school, status="scheduled").first()

    if request.method == 'POST':
        form = AccreditationApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            if not accreditation:
                accreditation = Accreditation.objects.create(school=school, status="scheduled")

            if not accreditation.visit_start_date:
                accreditation.visit_start_date = application.site_visit_start_date
            if not accreditation.visit_end_date:
                accreditation.visit_end_date = application.site_visit_end_date
            accreditation.save()

            return redirect('edit_accreditation', accreditation.id)
    else:
        form = AccreditationApplicationReviewForm(instance=application)

    context = dict(school=school,application=application, form=form, info_page=info_page)
    return render(request, 'accreditation/accreditation_application_review.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def accreditation_application_list(request):
    applications = AccreditationApplication.objects.all().order_by('-date')
    context=dict(applications = applications)
    return render (request, 'accreditation/accreditation_application_list.html', context)
