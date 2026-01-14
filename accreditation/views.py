from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch

from selfstudy.models import SelfStudy
from users.decorators import allowed_users
from django.contrib import messages

from .models import *
from .forms import *
from users.models import SchoolType
from annualvisit.models import SchoolDocument
from emailing.functions import send_simple_email
from services.models import Resource

#ISEI Views

def isei_standards_indicators(request, school_id=None):

    if request.user.is_authenticated:
        guest=False
    else:
        guest=True

    selected_school_type_ids = request.GET.getlist("school_type")

    if school_id:
        school = get_object_or_404(School, pk=school_id)
        indicators_qs = Indicator.objects.filter(active=True, school_type__in=school.school_type.all())
    else:
        school=None
        if selected_school_type_ids:
            indicators_qs = Indicator.objects.filter(
                active=True,
                school_type_id__in=selected_school_type_ids
            )
        else:
            indicators_qs = Indicator.objects.filter(active=True)


    indicator_prefetch = Prefetch(
        'indicator_set',
        queryset=indicators_qs,
        to_attr='filtered_indicators'
    )

    standards = (
        Standard.objects.top_level()
        .prefetch_related(
            indicator_prefetch,
            Prefetch(
                'substandards',
                queryset=Standard.objects.prefetch_related(indicator_prefetch)
            )
        )
    )


    context = dict(standards=standards, school=school, guest=guest,
                   school_types=SchoolType.objects.all().order_by('code'),
                   selected_school_type_ids=selected_school_type_ids,
                   )
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
@allowed_users(allowed_roles=['principal', 'registrar', 'staff', 'coordinating_team'])
def school_accreditation_dashboard(request, school_id):
    school=get_object_or_404(School, id=school_id)


    #For a new school create an accreditation document folder directly, instead of an annual visit one
    #The Link will be stored in SchoolDocuments though, were the Annual Visit Document links usually are
    #The logic is that a new school should prepare for accreditation all along
    #When creating their first accreditation we will use that link
    if Accreditation.objects.filter(school=school).exists():
        new_school=False
        school_doc = None
    else:
        new_school=True
        school_doc=SchoolDocument.objects.filter(school=school).first()

    today = timezone.localdate()

    # 1️⃣ Get all applications for the school
    applications = AccreditationApplication.objects.filter(school=school)

    # 2️⃣ Check for an application not attached to any accreditation
    in_progress_app = applications.filter(accreditation__isnull=True).first()

    # 3️⃣ Check for an application attached to a scheduled accreditation
    scheduled_app = applications.filter(accreditation__status=Accreditation.AccreditationStatus.SCHEDULED).first()

    # 4️⃣ Determine status
    if in_progress_app:
        application_status = "progress"  # In Progress
    elif scheduled_app:
        application_status = "scheduled"  # Scheduled
    else:
        application_status = "apply"  # Needs to apply

    accreditation_scheduled = Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.SCHEDULED).first()
    current_selfstudy = SelfStudy.objects.filter(accreditation=accreditation_scheduled).first()

    #accreditation_active = Accreditation.objects.filter(status=Accreditation.AccreditationStatus.ACTIVE).first()
    #accreditation_past = Accreditation.objects.filter(status=Accreditation.AccreditationStatus.PAST)

    evidence_list=Resource.objects.filter(name="Required Evidence List").first()

    accreditation_groups = {
        "scheduled": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.SCHEDULED),
        "active": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.ACTIVE),
        "past": Accreditation.objects.filter(school=school, status=Accreditation.AccreditationStatus.PAST),
    }

    context = dict(accreditation_groups =accreditation_groups, school=school,
                   application_status = application_status, current_selfstudy=current_selfstudy,
                   new_school=new_school, school_doc=school_doc,
                   evidence_list=evidence_list)

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
            print("lowest_grade")
            if app.lowest_grade == "K" or app.lowest_grade == "PreK":
                grade = 0
            else:
                grade=int(app.lowest_grade)
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

    # 1️⃣ Get all applications for the school
    applications = AccreditationApplication.objects.filter(school=school)

    # 3️⃣ Check for an application attached to a scheduled accreditation
    scheduled_app = applications.filter(accreditation__status=Accreditation.AccreditationStatus.SCHEDULED).first()
    if scheduled_app:
        in_progress_app = scheduled_app
    else:
        # 2️⃣ Check for an application not attached to any accreditation
        in_progress_app = applications.filter(accreditation__isnull=True).first()

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
                 address_form = address_form, postal_address_form = postal_address_form,
                 application=in_progress_app,)

    return render(request, 'accreditation/accreditation_application.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def accreditation_application_review(request, pk):
    info_page = InfoPage.objects.filter(slug="accreditation-application-intro").first()
    application = get_object_or_404(AccreditationApplication, pk=pk)
    school=application.school


    accreditation = application.accreditation
    if not accreditation:
        accreditation = Accreditation.objects.filter(school=school, status="scheduled").first()

        if not accreditation:
            accreditation = Accreditation.objects.create(school=school, status=Accreditation.AccreditationStatus.SCHEDULED)

        application.accreditation = accreditation
        application.save()

    if not accreditation.school_year:
        accreditation.school_year = application.school_year
        accreditation.save()

    if request.method == 'POST':
        form = AccreditationApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
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


def required_evidence_list(request):
    categories = RequiredEvidenceCategory.objects.prefetch_related("requiredevidence_set").all()

    context = dict(
        categories=categories,
        guest=request.GET.get("guest"),  # mimic your template conditions
        school=None,  # mimic your standards template (can pass actual school later if needed)
    )
    return render(request, "accreditation/required_evidence_list.html", context)

@login_required(login_url='login')
def my_accreditations(request, user_id):
    user = User.objects.get(pk=user_id)
    accreditations = Accreditation.objects.filter(
        visiting_team_membership__user=user,
        visiting_team_membership__active=True,
        status=Accreditation.AccreditationStatus.SCHEDULED,
    ).prefetch_related(
        Prefetch(
            "visiting_team_membership",
            queryset=AccreditationVisitingTeam.objects.filter(active=True).select_related("user")
        )
    ).distinct()

    team_materials=Resource.objects.filter(name='Accreditation Team Materials').first()

    context = dict(
        accreditations=accreditations, team_materials=team_materials,
    )
    return render(request, "accreditation/my_accreditations.html", context)
