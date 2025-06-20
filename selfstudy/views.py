from dis import Instruction

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from users.utils import is_in_any_group
from django.contrib import messages

from django.db.models import Max, Count, Q
from django.contrib.auth.models import Group
from django.utils import timezone
from collections import defaultdict
import json

from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users

from users.utils import is_in_any_group
from users.models import UserProfile
from .forms import *
from accreditation.models import Standard, Indicator, Level
from teachercert.models import SchoolYear
from apr.models import APR, ActionPlan
from reporting.models import AnnualReport, Closing, Opening, Personnel, StaffStatus, StaffCategory, LongitudinalEnrollment, Student, GRADE_LEVEL_DICT
from .models import *

from teachercert.myfunctions import newest_certificate

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='login')
def check_lock(request, form_id):
    """Returns JSON indicating whether the form is locked by another user."""
    CurrentlyEditing.remove_stale_entries()
    active_locks = CurrentlyEditing.objects.filter(form_id=form_id).exclude(user=request.user).first()
    if active_locks:
        return JsonResponse({"locked": True, "username": f"{active_locks.user.first_name} {active_locks.user.last_name}" })
    return JsonResponse({"locked": False})

@login_required(login_url='login')
def acquire_lock(request, form_id):
    """Acquire a lock on the form."""
    CurrentlyEditing.objects.update_or_create(user=request.user, form_id=form_id, defaults={"last_active": now()})
    return JsonResponse({"status": "locked"})

@csrf_exempt
@login_required(login_url='login')
def release_lock(request, form_id):
    """Release the lock when the user leaves the page."""
    CurrentlyEditing.objects.filter(user=request.user, form_id=form_id).delete()
    return JsonResponse({"status": "released"})


#Creating the self-study views
def get_or_create_selfstudy(accreditation):
    selfstudy, created = SelfStudy.objects.get_or_create(
        accreditation=accreditation,
    )
    return selfstudy

def setup_coordinating_team(selfstudy, standards):
    """ Creates a general coordinating team for the given self-study and a team for each standard in the standards list. """
    general_team, created = SelfStudy_Team.objects.get_or_create(selfstudy=selfstudy, standard=None)
    for standard in standards:
        team, created = SelfStudy_Team.objects.get_or_create(selfstudy=selfstudy, standard=standard)

def setup_school_profile(selfstudy):
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)

    # Create entries for FinancialTwoYearDataEntries for all active keys
    for data_key in FinancialTwoYearDataKey.objects.filter(active=True):
        FinancialTwoYearDataEntry.objects.get_or_create(
            school_profile=school_profile,
            data_key=data_key,
        )
    # Create entries for FinancialAdditionalDataEntries for all active keys
    for data_key in FinancialAdditionalDataKey.objects.filter(active=True):
        FinancialAdditionalDataEntry.objects.get_or_create(
            school_profile=school_profile,
            data_key=data_key,
        )

    # Create entries for FullTimeEquivalency for all keys
    for assignment in FTEAssignmentKey.objects.filter(active=True):
        FullTimeEquivalency.objects.get_or_create(
            school_profile=school_profile,
            assignment=assignment,
        )

def setup_indicator_evaluations(selfstudy):
    """
    Creates IndicatorEvaluation objects for all active Indicators associated with
    the SelfStudy's accreditation standards, in bulk. Ensures no duplicates are created.
    """
    # Get the school object first
    school = selfstudy.accreditation.school

    # Filter the indicators where the school_type of the indicator is in the school's school_types
    indicators = Indicator.objects.filter(active=True, school_type__in=school.school_type.all()).select_related('standard')

    if not indicators.exists():
        raise ValueError("No active indicators found. Ensure that indicators are properly configured.")

    # Fetch existing evaluations for this selfstudy
    existing_evaluations = IndicatorEvaluation.objects.filter(selfstudy=selfstudy).values_list('indicator_id', flat=True)
    # Filter indicators to exclude those already evaluated
    new_indicators = indicators.exclude(id__in=existing_evaluations)

    if not new_indicators.exists():
        return 0  # No new evaluations to create

    indicator_evaluations = [ # Prepare a list to hold new IndicatorEvaluation objects
        IndicatorEvaluation(
            selfstudy=selfstudy, indicator=indicator, standard=indicator.standard,
            score=None,  reference_documents=None, explanation=None,
        )
        for indicator in new_indicators
    ]

    indicator_evaluations.sort(key=lambda x: x.indicator.code) # Sort the evaluations by indicator code (if needed)
    IndicatorEvaluation.objects.bulk_create(indicator_evaluations) # Bulk create the new evaluations

    #return len(indicator_evaluations)  # Optionally return the count of created objects

def setup_standard_evaluation(selfstudy, standards):
    # Create StandardEvaluation objects for the selfstudy
    for standard in standards:
        standard, created= StandardEvaluation.objects.get_or_create(selfstudy=selfstudy,standard=standard,)
        #if created:
         #   print(standard)

@login_required(login_url='login')
def setup_selfstudy(request, accreditation_id):
    # Retrieve the Accreditation object by ID
    accreditation = get_object_or_404(Accreditation, id=accreditation_id)
    selfstudy = get_or_create_selfstudy(accreditation)

    standards = Standard.objects.top_level()

    setup_coordinating_team(selfstudy, standards)
    setup_school_profile(selfstudy)
    setup_standard_evaluation(selfstudy, standards)
    setup_indicator_evaluations(selfstudy)

    context = dict(selfstudy=selfstudy, standards=standards)

    return render(request, 'selfstudy/selfstudy.html', context)

@login_required(login_url='login')
def selfstudy(request, selfstudy_id):
    try:
        # Try to retrieve the existing SelfStudy object
        selfstudy = SelfStudy.objects.get(id=selfstudy_id)
        standards = Standard.objects.top_level()

        if is_in_any_group(request.user, ['staff', 'principal', 'registrar']):
            school_privileges = True
        else:
            school_privileges = False

        if is_in_any_group(request.user, ['staff']):
            isei_privilages=True
        else:
            isei_privilages=False


        if request.method == "POST":
            if "submit_selfstudy" in request.POST:
                selfstudy.submission_date = timezone.now().date()
            elif "reopen_selfstudy" in request.POST:
                selfstudy.submission_date = None
            selfstudy.save()
            return redirect('selfstudy', selfstudy_id=selfstudy.id)  # Reload the page after submission

        context = dict(selfstudy=selfstudy, standards=standards, active_link="selfstudy",
                       school_privileges=school_privileges, isei_privileges=isei_privilages )
        return render(request, 'selfstudy/selfstudy.html', context)

    except SelfStudy.DoesNotExist:
        # If no SelfStudy is found, redirect to setup_selfstudy
        accreditation = get_object_or_404(Accreditation, id=selfstudy_id)  # Assuming the selfstudy_id matches accreditation_id
        return setup_selfstudy(request, accreditation_id=accreditation.id)



#School filling out the self study views

@login_required(login_url='login')
def selfstudy_standard(request, selfstudy_id, standard_id, readonly=False):

    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards = Standard.objects.top_level()
    standard = get_object_or_404(Standard, id=standard_id, parent_standard__isnull=True)
    form_id = f"{selfstudy.id}_standard_{standard_id}"

    evidence_list = standard.evidence.split(';') if standard.evidence else []
    narrative = StandardNarrative.objects.first()
    standard_evaluation, created = StandardEvaluation.objects.get_or_create(selfstudy=selfstudy, standard=standard)

    substandards = standard.substandards.all()
    grouped_data = []
    if substandards.exists():
        substandards_exist=True
        for substandard in substandards:
            evaluations = IndicatorEvaluation.objects.filter(selfstudy=selfstudy, standard=substandard)
            indicators = Indicator.objects.filter(standard=substandard, active=True)

            grouped_data.append({
                "standard": substandard,
                "indicators": indicators,
                "evaluations": evaluations,
            })
        # Evidence is specific to the main standard
    else:
        substandards_exist=False
        evaluations = IndicatorEvaluation.objects.filter(selfstudy=selfstudy, standard=standard)
        indicators = Indicator.objects.filter(standard=standard, active=True)

        grouped_data.append({
            "standard": standard,
            "indicators": indicators,
            "evaluations": evaluations,
        })

        # Handle the MissionAndObjectives form in the same way as the standard form
    mission_and_objectives = MissionAndObjectives.objects.filter(selfstudy=selfstudy).first()

    if request.method == "POST":
        formset = IndicatorEvaluationFormSet(request.POST, queryset=IndicatorEvaluation.objects.filter(
            selfstudy=selfstudy, standard__in=[standard] + list(substandards) ))
        standard_form = StandardEvaluationForm(request.POST, instance=standard_evaluation)
        if standard.name == "Mission, Philosophy, Goals, & Objectives":
            mission_form = MissionAndObjectivesForm(request.POST, instance=mission_and_objectives)
        else:
            mission_form = None

        if formset.is_valid() and standard_form.is_valid():
            for form in formset:
                if form.is_valid():
                    # Manually set the indicator_score from the form data
                    # Manually get the indicator_score value from POST data
                    indicator_score_id = request.POST.get(f'{form.prefix}-indicator_score')
                    if indicator_score_id:
                        # Assign the selected IndicatorScore to the form instance
                        form.instance.indicator_score = IndicatorScore.objects.get(id=indicator_score_id)

                    form.save()
            formset.save()
            standard_form.save()

            if mission_form:
                if mission_form.is_valid():
                    mission_and_objectives = mission_form.save(commit=False)
                    mission_and_objectives.selfstudy = selfstudy  # Associate with the correct SelfStudy instance
                    mission_and_objectives.save()

            messages.success(request, "Your changes have been successfully saved!")
        else:
            messages.error(request, "Some of your changes were not saved!")

            context = dict(selfstudy=selfstudy, standards = standards, standard=standard,
                           active_link=standard_id, evidence_list=evidence_list, narrative=narrative,
                           formset = formset, standard_form=standard_form,
                           grouped_data = grouped_data, substandards_exist=substandards_exist,
                           )

            return render(request, 'selfstudy/standard.html', context)
    else:
        formset = IndicatorEvaluationFormSet(queryset=IndicatorEvaluation.objects.filter(selfstudy=selfstudy,
                                                 standard__in=[standard] + list(substandards)))
        standard_form = StandardEvaluationForm(instance=standard_evaluation)
        if standard.name == "Mission, Philosophy, Goals, & Objectives":
            mission_form = MissionAndObjectivesForm(instance=mission_and_objectives)
        else: mission_form = None

    score_options = IndicatorScore.objects.all()

    if readonly:
        for form in formset:
            for field in form.fields.values():
                field.disabled = True
        for field in standard_form.fields.values():
            field.disabled = True
        if mission_form:
            for field in mission_form.fields.values():
                field.disabled = True


    context = dict(selfstudy=selfstudy, standards = standards, standard=standard,
                   formset = formset, standard_form=standard_form, mission_form=mission_form,
                   active_link=standard_id, evidence_list=evidence_list, narrative=narrative,
                   grouped_data = grouped_data, substandards_exist=substandards_exist,
                   form_id=form_id,
                   score_options=score_options,
                   readonly=readonly)

    return render(request, 'selfstudy/standard.html', context)

@login_required(login_url='login')
def selfstudy_actionplan_instructions(request, selfstudy_id):

    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards= Standard.objects.top_level()
    accreditation = Accreditation.objects.get(selfstudy=selfstudy)
    instructions = ActionPlanInstructions.objects.first()

    if accreditation:
        actionplans = ActionPlan.objects.filter(accreditation=accreditation).order_by('number')
    else:
        actionplans = None

    active_link = "actionplans"

    context=dict(actionplans=actionplans, active_link=active_link, accreditation_id=accreditation.id,
                 selfstudy=selfstudy, standards=standards, instructions=instructions)

    return render(request, 'selfstudy/action_plan_instructions.html', context)

@login_required(login_url='login')
def selfstudy_actionplan(request, accreditation_id, action_plan_id=None, readonly=False):
    accreditation = get_object_or_404(Accreditation, id=accreditation_id)

    selfstudy = get_object_or_404(SelfStudy, accreditation=accreditation)
    standards= Standard.objects.top_level()
    actionplans = ActionPlan.objects.filter(accreditation=accreditation).order_by('number')

    # Get the ActionPlan if updating, otherwise create a new one
    if action_plan_id:
        action_plan = get_object_or_404(ActionPlan, id=action_plan_id, accreditation=accreditation)
    else:
        action_plan = ActionPlan(accreditation=accreditation)

    form_id = f"{selfstudy.id}_actionplan_{action_plan.id}"

    # Inline formset to manage ActionPlanSteps with ActionPlan
    ActionPlanStepsFormSet = inlineformset_factory(ActionPlan, ActionPlanSteps, form=ActionPlanStepsForm, extra=10,
                                                   can_delete=True)
    formset=ActionPlanStepsFormSet(instance=action_plan)

    if request.method == 'POST':
        if 'delete' in request.POST and action_plan.id:
            #print("delete",action_plan)
            action_plan.delete()
            return HttpResponseRedirect(reverse('selfstudy_actionplan_instructions', kwargs={'selfstudy_id': selfstudy.id}))
        else:
            ap_form = ActionPlanForm(request.POST, instance=action_plan)
            formset = ActionPlanStepsFormSet(request.POST, instance=action_plan)

            if ap_form.is_valid():
                action_plan = ap_form.save()
                if formset.is_valid():
                    existing_steps = ActionPlanSteps.objects.filter(action_plan=action_plan)
                    max_number = existing_steps.aggregate(Max('number'))['number__max'] or 0

                    steps = formset.save(commit=False)
                    for i, step in enumerate(steps, start=max_number + 1):
                        if step.number is None:  # Only assign number if it doesn't already have one
                            step.number = i
                        step.action_plan = action_plan  # Link the step to the ActionPlan
                        step.save()
                    messages.success(request, "Action Plan has been successfully saved!")
                else:
                    messages.error(request, "Action Plan was not saved!")

                    #This might be needed if existing steps need renumbering
                    #for i, step in enumerate(existing_steps, start=1):
                    #    step.number = i
                    #    step.save()

                    #TODO  deal with progress_record creation when action plans is moved from self study to apr
                    #create_progress_records(apr, ActionPlan)

                #return redirect('manage_apr', accreditation.id)  # Redirect to APR detail page
    else:
        ap_form = ActionPlanForm(instance=action_plan)
        if readonly:
            ActionPlanStepsFormSet = inlineformset_factory(ActionPlan, ActionPlanSteps, form=ActionPlanStepsForm,
                                                           extra=0, can_delete=True)
            formset = ActionPlanStepsFormSet(instance=action_plan)

    if readonly:
        for field in ap_form.fields.values():
            field.disabled = True
        for form in formset:
            for field in form.fields.values():
                field.disabled=True

    context = dict(ap_form=ap_form, formset=formset, action_plan=action_plan, accreditation_id=accreditation_id,
                   selfstudy=selfstudy,standards=standards,
                   active_link=action_plan.id, actionplans=actionplans, form_id=form_id)

    return render(request, 'selfstudy/action_plan.html', context)

@login_required(login_url='login')
def selfstudy_coordinating_team(request, selfstudy_id, readonly=False):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards= Standard.objects.top_level()

    if is_in_any_group(request.user, ['staff','principal','registrar']):
        privileges=True
    else:
        privileges=False

    teams = SelfStudy_Team.objects.filter(selfstudy=selfstudy)

    context=dict(selfstudy=selfstudy, standards=standards, active_link="coordinating_team",
                 teams=teams, privileges=privileges, readonly=readonly)
    return render(request, 'selfstudy/coordinating_team.html', context)

@login_required(login_url='login')
def add_coordinating_team_members(request, selfstudy_id, team_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    team = get_object_or_404(SelfStudy_Team, id=team_id, selfstudy=selfstudy)

    #to get current staff as possible team members
    last_annual_report = AnnualReport.objects.filter(school=selfstudy.accreditation.school, report_type__code="ER").order_by('-submit_date').first()

    # Get all personnel from the school's last annual report
    school_personnel = Personnel.objects.filter(annual_report=last_annual_report).exclude(status=StaffStatus.NO_LONGER_EMPLOYED
            ).exclude(email_address__isnull=True).exclude(email_address__exact=''
            ).values('id','first_name', 'last_name', 'email_address')

    inactive_users = []  # Personnel with associated users that are inactive
    personnel_without_users = []  # Personnel with no associated users

    for personnel in school_personnel:
        user = User.objects.filter(first_name=personnel['first_name'],last_name=personnel['last_name'],
            email=personnel['email_address']).first()
        if user:
            if not user.is_active:
                inactive_users.append({
                    'id': personnel['id'],
                    'first_name': personnel['first_name'],
                    'last_name': personnel['last_name'],
                    'email': personnel['email_address'],
                    'user_id': user.id,
                })
        else:
            personnel_without_users.append({
                'id': personnel['id'],
                'first_name': personnel['first_name'],
                'last_name': personnel['last_name'],
                'email': personnel['email_address'],
            })

    # in the SelfStudy_TeamMemberForm we query the users from this school that have active account
    form = SelfStudy_TeamMemberForm(request.POST or None, selfstudy=selfstudy, team=team)

    # Handle form submission
    if request.method == 'POST':
        if form.is_valid():
            form.save(team)  # Save members to the team

            selected_personnel_without_users_ids = request.POST.getlist('personnel_without_users')
            selected_inactive_users_ids = request.POST.getlist('inactive_users')

            # Create users for the selected personnel without user
            personnel_dict = {p['id']: p for p in personnel_without_users}
            for personnel_id in selected_personnel_without_users_ids:
                personnel = personnel_dict.get(int(personnel_id))
                if personnel:
                    # Create a new user
                    user = User.objects.create_user(
                        username=f"{personnel['first_name']}.{personnel['last_name']}",
                        email=personnel['email'],
                        first_name=personnel['first_name'],
                        last_name=personnel['last_name']
                    )
                    profile = UserProfile.objects.create(user=user, school=school)
                    SelfStudy_TeamMember.objects.create(user=user, team=team)
                    user.groups.add(Group.objects.get(name="coordinating_team"))

            # Reactivate users and add second group to the team
            for user_data in inactive_users:
                if str(user_data['id']) in selected_inactive_users_ids:
                    user = User.objects.get(id=user_data['user_id'])
                    user.is_active = True
                    user.save()
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.school = school
                    profile.save()
                    # Create TeamMember for this personnel
                    SelfStudy_TeamMember.objects.create(user=user, team=team)
                    user.groups.add(Group.objects.get(name="coordinating_team"))

            return redirect('selfstudy_coordinating_team', selfstudy_id=selfstudy.id)


    context = dict(form=form, selfstudy=selfstudy, team=team, standards=standards,
                   active_link="coordinating_team", report_id = last_annual_report.id,
                   personnel_without_users=personnel_without_users,
                   inactive_users =inactive_users,)

    return render(request, 'selfstudy/add_coordinating_team_members.html', context)

@login_required(login_url='login')
def selfstudy_profile(request, selfstudy_id, readonly=False):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards = Standard.objects.top_level()
    form_id=f"{selfstudy.id}_profile"

    # Retrieve or create the SchoolProfile
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)

    school = selfstudy.accreditation.school
    address = school.street_address

    # Populate missing fields from other sources
    if not school_profile.school_name:
        school_profile.school_name = school.name
    if not school_profile.address:
        school_profile.address =address.address_1
        school_profile.city = address.city
        school_profile.state_us = address.state_us
        school_profile.zip_code = address.zip_code
        school_profile.country = address.country
    if not school_profile.principal:
        school_profile.principal = school.principal
    if not school_profile.board_chair:
        school_profile.board_chair = school.board_chair
    if not school_profile.last_evaluation:
        school_profile.last_evaluation = school.current_accreditation().visit_date_range()
    if not school_profile.last_interim:
        school_profile.last_interim = ""  # Set a default value

    # Save only if new data was added
    school_profile.save()

    # Handle form submission
    if request.method == "POST":
        form = SchoolProfileForm(request.POST, instance=school_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)  # Get updated profile but don't save it to DB just yet

            # Check if any fields were updated, and if so, update the other models
            if updated_profile.school_name != school.name:
                school.name = updated_profile.school_name
                school.save()

            if updated_profile.address != address.address_1:
                address.address_1 = updated_profile.address
                address.city = form.cleaned_data.get('city')
                address.state_us = form.cleaned_data.get('state_us')
                address.zip_code = form.cleaned_data.get('zip_code')
                address.country = form.cleaned_data.get('country')
                address.save()

            if updated_profile.principal != school.principal:
                school.principal = updated_profile.principal
                school.save()

            if updated_profile.board_chair != school.board_chair:
                school.board_chair = updated_profile.board_chair
                school.save()

            # Save the updated school_profile now that we've made changes
            school_profile.save()

            messages.success(request, "Changes have been successfully saved!")
        else:
            messages.error(request, "Some changes were not saved!")

    else:
        form = SchoolProfileForm(instance=school_profile)

    if readonly: # Disable all fields in the form when readonly is True
        for field in form.fields.values():
            field.disabled = True

    context= dict(selfstudy=selfstudy, standards = standards,
                   active_link="profile", active_sublink="general_info",
                    form=form, form_id=form_id,
                    readonly=readonly)

    return render(request, "selfstudy/profile.html", context )


@login_required(login_url='login')
def profile_history(request, selfstudy_id, readonly=False):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()
    form_id= f"{selfstudy.id}_history"

    history_form = SchoolHistoryForm(instance=school_profile)

    if request.method == 'POST':
        history_form = SchoolHistoryForm(request.POST, instance=school_profile)
        if history_form.is_valid():
            history_form.save()
            messages.success(request, "School history has been successfully saved!")
        else:
            messages.error(request,"School history was not saved!")

    if readonly: # Disable all fields in the form when readonly is True
        for field in history_form.fields.values():
            field.disabled = True

    context = dict(selfstudy=selfstudy, standards = standards,
                   history_form = history_form,
                   active_sublink="history", active_link="profile",
                   form_id=form_id,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_history.html', context)

@login_required(login_url='login')
def profile_financial(request, selfstudy_id, readonly=False):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_financial"

    # Query related financial data entries
    two_year_data_queryset = FinancialTwoYearDataEntry.objects.filter(school_profile=school_profile)
    additional_data_queryset = FinancialAdditionalDataEntry.objects.filter(school_profile=school_profile)


    if request.method == 'POST':
        two_year_formset = FinancialTwoYearDataFormSet(request.POST or None, queryset=two_year_data_queryset, prefix="two_years")
        additional_formset = FinancialAdditionalDataFormSet(request.POST or None, queryset=additional_data_queryset, prefix="additional")

        if two_year_formset.is_valid():
            if any(form.has_changed() for form in two_year_formset):
                two_year_formset.save()
                messages.success(request, "2-Year Financial Data has been successfully saved!")
            else:
                messages.info(request, "No changes made to 2-Year Financial Data")
        else:
            messages.error(request, "Some 2-year Financial Data was not saved!")

        if additional_formset.is_valid():
            if any(form.has_changed() for form in additional_formset):
                additional_formset.save()
                messages.success(request, "Additional Financial Data has been successfully saved!")
            else:
                messages.info(request, "No changes made to Additional Financial Data")
        else:
            messages.error(request, "Some Additional Financial Data was not saved!")

    # Initialize formsets
    two_year_formset = FinancialTwoYearDataFormSet(queryset=two_year_data_queryset, prefix="two_years")
    additional_formset = FinancialAdditionalDataFormSet(queryset=additional_data_queryset, prefix="additional")

    if readonly: # Disable all fields in the form when readonly is True
        for subform in two_year_formset:
            for field in subform.fields.values():
                field.disabled = True
        for subform in additional_formset:
            for field in subform.fields.values():
                field.disabled = True

    context = dict(selfstudy=selfstudy, standards = standards, active_sublink="financial", active_link="profile",
                    two_year_formset = two_year_formset, additional_formset = additional_formset,
                   form_id=form_id,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_financial.html', context)


#helper functions for Profile Personnel
@login_required(login_url='login')
def import_personnel_data(request, school_profile, annual_report):
    """Imports personnel data from the latest annual report."""
    if not annual_report:
        messages.error(request, "Employee Report for this school not found!")
        return

    active_personnel = annual_report.personnel_set.exclude(status=StaffStatus.NO_LONGER_EMPLOYED)
    updated_ids = []

    for personnel in active_personnel:
        years_experience = max(personnel.years_work_experience or 0, personnel.years_teaching_experience or 0,
                               personnel.years_administrative_experience or 0)
        highest_degree = personnel.degrees.order_by('-rank').first()
        highest_degree_name = highest_degree.name if highest_degree else None

        ss_personnel, created = SelfStudyPersonnelData.objects.update_or_create(
            school_profile=school_profile,
            first_name=personnel.first_name,
            last_name=personnel.last_name,
            defaults={
                'status': personnel.status,
                'years_experience': years_experience,
                'years_at_this_school': personnel.years_at_this_school,
                'highest_degree': highest_degree_name,
                'gender': personnel.gender,
            }
        )

        ss_personnel.position.set(personnel.positions.all())

        if personnel.teacher:
            newest_cert = newest_certificate(personnel.teacher)
            if newest_cert:
                endorsements = [e.endorsement.name for e in newest_cert.tendorsement_set.all()]
                ss_personnel.certification = newest_cert.certification_type.name
                ss_personnel.cert_renewal_date = newest_cert.renewal_date
                ss_personnel.endorsements = ', '.join(endorsements)

        ss_personnel.save()
        updated_ids.append(ss_personnel.id)

    SelfStudyPersonnelData.objects.filter(school_profile=school_profile).exclude(id__in=updated_ids).delete()

    messages.success(request, "Personnel was successfully imported/updated!")

@login_required(login_url='login')
def handle_fte_data(request, school_profile, fte_queryset):
    """Handles FTE data form submission."""
    FTE_formset = FTEFormSet(request.POST, queryset=fte_queryset, prefix="fte")
    fte_equivalency_form = FTEEquivalencyForm(request.POST, instance=school_profile)

    if FTE_formset.is_valid():
        if any(form.has_changed() for form in FTE_formset):
            FTE_formset.save()
            if "fte-data" in request.POST or "submit-all" in request.POST:
                messages.success(request, "Full Time Equivalency Data has been successfully saved!")
    else:
        messages.error(request, "Some Full Time Equivalency Data was not saved!")

    if fte_equivalency_form.is_valid():
        if fte_equivalency_form.has_changed():
            fte_equivalency_form.save()
            if "fte-data" in request.POST or "submit-all" in request.POST:
                messages.success(request, "FTE Student Ratio has been successfully saved!")
    else:
        messages.error(request, "FTE Student Ratio was not saved!")

    if not list(messages.get_messages(request)):
        if "fte-data" in request.POST or "submit-all" in request.POST:
            messages.info(request, "No changes were made in FTE Data.")

    return FTEFormSet(queryset=fte_queryset, prefix="fte"), FTEEquivalencyForm(instance=school_profile)

@login_required(login_url='login')
def profile_personnel(request, selfstudy_id, readonly=False):
    """Main personnel profile view, handling personnel data and FTE data."""
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_personnel"

    accreditation_school_year = selfstudy.accreditation.school_year

    #get the accreditation year annual_report to import data from
    annual_report = AnnualReport.objects.filter(school=school, report_type__code="ER", school_year= accreditation_school_year).first()

    arID=annual_report.id or None
    ar_school_year=annual_report.school_year or None

    FTE_formset = FTEFormSet(queryset=FullTimeEquivalency.objects.filter(school_profile=school_profile), prefix="fte")
    fte_equivalency_form = FTEEquivalencyForm(instance=school_profile)

    pga_formset=ProfessionalActivityFormSet(instance=school_profile)

    #import_personnel and fte-data functions are defined above
    if request.method == "POST":
        if "import_personnel" in request.POST:
            import_personnel_data(request, school_profile, annual_report) #Functions above to handle this and the next one

        #I will save it all for each submit to avoid loosing data
        else:
            FTE_formset, fte_equivalency_form = handle_fte_data(request, school_profile, FullTimeEquivalency.objects.filter(school_profile=school_profile))

            pga_formset = ProfessionalActivityFormSet(request.POST, instance=school_profile)
            if pga_formset.is_valid():
                if any(form.has_changed() for form in pga_formset):
                    pga_formset.save()
                    if "pga" in request.POST or "submit-all" in request.POST:
                        messages.success(request, "Professional Activity Data has been successfully saved!")
                else:
                    if "pga" in request.POST or "submit-all" in request.POST:
                        messages.info(request, "No changes in Professional Activity Data")
            else:
                messages.error(request, "Some Professional Activity Data was not saved!")



    #Personnel Data to be displayed (was imported with "import_personnel"
    personnel_data = SelfStudyPersonnelData.objects.filter(school_profile__selfstudy=selfstudy)
    if personnel_data:
        personnel_imported = True
    else:
        personnel_imported = False

    teaching_admin_positions = StaffPosition.objects.filter(
        category__in=[StaffCategory.TEACHING, StaffCategory.ADMINISTRATIVE]).exclude(
        name="Practical Arts/Life Skills Teacher")
    admin_academic_dean = personnel_data.filter(position__in=teaching_admin_positions).distinct()
    vocational_instructors = personnel_data.filter(position__name="Practical Arts/Life Skills Teacher").exclude(
        id__in=admin_academic_dean.values_list('id', flat=True))
    non_instructional = (personnel_data.filter(Q(position__category=StaffCategory.GENERAL_STAFF))
                         .exclude(id__in=admin_academic_dean.values_list('id', flat=True)) \
                         .exclude(id__in=vocational_instructors.values_list('id', flat=True)).distinct())


    # Count men and women in each degree category
    degree_gender_counts = personnel_data.values('highest_degree', 'gender') \
        .annotate(gender_count=Count('id'),).order_by('highest_degree', 'gender')
    # Prepare the data into a dictionary for easy display
    degree_gender_dict = {}

    for item in degree_gender_counts:
        degree = item['highest_degree']
        gender = item['gender']
        count = item['gender_count']

        if degree not in degree_gender_dict:
            degree_gender_dict[degree] = {'M': 0, 'F': 0}

        degree_gender_dict[degree][gender] = count

    if readonly:  # Disable all fields in the form when readonly is True
        ProfessionalActivityFormSetReadonly = inlineformset_factory(SchoolProfile,ProfessionalActivity,
            form=ProfessionalActivityForm,extra=0)
        pga_formset = ProfessionalActivityFormSetReadonly(instance=school_profile, prefix='pga')

        for subform in pga_formset:
            for field in subform.fields.values():
                field.disabled = True
        for subform in FTE_formset:
            for field in subform.fields.values():
                field.disabled = True

    # Get last 5 school-years retention data
    start_year = int(accreditation_school_year.name.split('-')[0]) # 1. Extract last 5 school year names
    year_names = [f"{start_year - i}-{start_year + 1 - i}" for i in range(5)][::-1]

    school_years = SchoolYear.objects.filter(name__in=year_names)  # 2. Get SchoolYear objects

    # 3. Prefetch reports for those years
    reports = AnnualReport.objects.filter(school=school, report_type__code="ER", school_year__in=school_years).select_related('school_year')
    # 4. Map: {school_year_name: report}
    reports_by_year = {report.school_year.name: report for report in reports}
    # 5. Build retention data
    retention_data = []
    for year_name in year_names:
        report = reports_by_year.get(year_name)
        if report:
            retention_data.append({
                "year": year_name,
                "total": report.total_personnel(),
                "not_returned": report.not_returned_personnel(),
                "retention": report.retention_rate(),  # already a percentage
            })

    context = dict( selfstudy=selfstudy, standards=standards, active_sublink="personnel", active_link="profile",
        admin_academic_dean=admin_academic_dean, vocational_instructors=vocational_instructors, non_instructional=non_instructional,
        arID=arID, ar_school_year=ar_school_year, personnel_imported = personnel_imported,
        fte_formset=FTE_formset, fte_equivalency_form=fte_equivalency_form,
        degree_gender_dict=degree_gender_dict,
        pga_formset=pga_formset,
        form_id=form_id,
         readonly=readonly,
        retention_data=retention_data,
    )

    return render(request, 'selfstudy/profile_personnel.html', context)


from django.db.models import Count


def get_international_students_by_country(report, school_country):
    """
    Returns a list of dictionaries with country names and student counts
    for international students in the given report.

    Parameters:
    - report: the AnnualStudentReport instance
    - school_country: the country's name or ID (depends on your model)

    Returns:
    - A list like: [{'country': 'Canada', 'count': 5}, ...]
    """
    return Student.objects.filter(
        annual_report=report,
        status__in=['enrolled']
    ).exclude(
        country=school_country
    ).values('country__name').annotate(
        count=Count('id')
    ).order_by('-count')


@login_required(login_url='login')
def profile_student(request, selfstudy_id, readonly=False):

    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_student"

    # Get the current school year from the accreditation model
    accreditation_school_year = selfstudy.accreditation.school_year

#Get last 5 school-years
    start_year = int(accreditation_school_year.name.split('-')[0]) # Extract the start year from the 'name' field, which is in the format "2024-2025"
    previous_school_years = [f"{start_year - i}-{start_year + 1 - i}" for i in range(5)] # Generate the last 5 school year names (e.g., "2024-2025", "2023-2024", ...)
    previous_school_years = previous_school_years[::-1] # Reverse the order of years to have the current year last

# Fetch the enrollment data for the last 5 school years
    enrollment_data = LongitudinalEnrollment.objects.filter(school=school, year__name__in=previous_school_years).order_by('year', 'grade')

    # Get the valid grade levels for the school using the get_grade_range method
    valid_grades = school.get_grade_range()

    # Organize the data by grade and year
    enrollment_by_grade_and_year = {grade: {} for grade in valid_grades}

    # Populate the dictionary with the enrollment count for each grade and year
    for record in enrollment_data:
        grade = record.grade
        year_name = record.year.name
        if grade in valid_grades:  # Only add data for valid grades
            enrollment_by_grade_and_year[grade][year_name] = record.enrollment_count

#Get student demographics for previous 5 years
    student_data=[]

    school_country=school.street_address.country
    international=False

    for year in previous_school_years:
        annual_opening_report = AnnualReport.objects.filter(report_type__code="OR", school_year__name=year, school=school).first()
        opening = Opening.objects.filter(annual_report=annual_opening_report).first()

        if opening:
            annual_closing_report = AnnualReport.objects.filter(report_type__code="CR", school_year__name=year, school=school).first()
            closing = Closing.objects.filter(annual_report=annual_closing_report).first()

            annual_student_report = AnnualReport.objects.filter(report_type__code="SR", school_year__name=year,school=school).first()

            opening_enrollment = opening.opening_enrollment

            international_student_count = Student.objects.filter(annual_report=annual_student_report, status__in=['enrolled']).exclude(
                country=school_country).count()
            if opening_enrollment > 0:
                percent_international = round( international_student_count * 100 / opening_enrollment, 1)
            else:
                percent_international = 0

            international_countries = get_international_students_by_country(annual_student_report, school_country)
            if international_countries: international=True

            percent_female = opening.girl_percentage
            percent_male = opening.boy_percentage

            #not_returned = opening.did_not_return_count
            #withdrawn_count = closing.withdraw_count if closing else None

            withdrawn_percentage = closing.withdrawn_percentage if closing else None
            if opening_enrollment > 0:
                not_returned_percentage = 100 - opening.retention_percentage
                retention = round(opening.retention_percentage - withdrawn_percentage if withdrawn_percentage else opening.retention_percentage, 1)
            else:
                not_returned_percentage = None
                retention = None

            baptized_students = closing.baptized_students if closing else None

            student_data.append({
                'year': year,
                'opening_enrollment': opening_enrollment,
                'not_returned_percentage': not_returned_percentage,
                #'withdrawn_count': withdrawn_count,
                'withdrawn_percentage': withdrawn_percentage,
                'retention': retention,

                'percent_female': percent_female,
                'percent_male': percent_male,

                'baptized_students': baptized_students,
                'closing_report':annual_closing_report,
                'opening_report':annual_opening_report,
                'student_report':annual_student_report,

                'percent_international': percent_international,
                'international_countries':international_countries,
            })



#Get Baptismal Data per grade level for current year
    annual_report = AnnualReport.objects.filter(school=school, report_type__code="SR", school_year=accreditation_school_year).first()
    # Initialize the nested dict
    student_baptism_data = {
        grade: {
            'sda_home': {'baptized': 0, 'not_baptized': 0},
            'non_sda_home': {'baptized': 0, 'not_baptized': 0},
        }
        for grade in valid_grades
    }
    # Fetch all relevant students
    students = Student.objects.filter(annual_report=annual_report, status__in=["enrolled"])

    for student in students:
        grade = student.grade_level
        if grade not in student_baptism_data:
            continue  # skip irrelevant grades
        if student.parent_sda == 'Y':
            key = 'sda_home'
        elif student.parent_sda in ('N', 'O'):
            key = 'non_sda_home'
        else:
            continue  # skip if we don’t care about this row

        if student.baptized == 'Y':
            student_baptism_data[grade][key]['baptized'] += 1
        elif student.baptized in ('N', 'O'):
            student_baptism_data[grade][key]['not_baptized'] += 1

    grade_labels = {v: k for k, v in GRADE_LEVEL_DICT.items()}

    # Totals for enrollment data per year
    total_by_year = {year: 0 for year in previous_school_years}
    for grade in valid_grades:
        for year in previous_school_years:
            count = enrollment_by_grade_and_year.get(grade, {}).get(year, 0)
            total_by_year[year] += count

    # Totals for baptismal data
    total_baptism_data = {
        'sda_home': {'not_baptized': 0, 'baptized': 0},
        'non_sda_home': {'not_baptized': 0, 'baptized': 0},
    }

    for grade in valid_grades:
        grade_data = student_baptism_data.get(grade, {})
        for home_type in ['sda_home', 'non_sda_home']:
            for key in ['baptized', 'not_baptized']:
                total = grade_data.get(home_type, {}).get(key, 0)
                total_baptism_data[home_type][key] += total

    # Totals for summary stats
    total_students = 0
    non_sda_home_students = 0
    baptized_students = 0

    for student in students:
        total_students += 1
        if student.parent_sda in ('N', 'O'):
            non_sda_home_students += 1
        if student.baptized == 'Y':
            baptized_students += 1
    # Avoid division by zero
    percentage_non_sda_home = (non_sda_home_students / total_students * 100) if total_students else 0
    percentage_baptized = (baptized_students / total_students * 100) if total_students else 0



# Get or create the projected enrollment entry
    projected_data, created = StudentEnrollmentData.objects.get_or_create(school_profile=school_profile)

    if request.method == "POST" and "projected_enrollment_submit" in request.POST:
        form = StudentEnrollmentDataForm(request.POST, instance=projected_data)
        if form.is_valid():
            form.save()
            return redirect(request.path_info)  # or use ?next= like before
    else:
        form = StudentEnrollmentDataForm(instance=projected_data)


#Get or create student follow-up data
    levels = school.get_school_type() # Determine applicable levels (elementary, secondary) for this school

    followup_data_tables = {}

    for level in levels:
        keys = list(StudentFollowUpDataKey.objects.filter(level=level, active=True).order_by('order_number'))
        years = list(SchoolYear.objects.filter(name__in=previous_school_years[-3:]).order_by('name'))

        # Build a lookup for quick access to entries
        entries_lookup = {
            (year.id, key.id): StudentFollowUpDataEntry.objects.get_or_create(
                school=school,
                school_year=year,
                followup_data_key=key
            )[0]
            for year in years for key in keys
        }

        # Build row-wise table data
        rows = []
        for year in years:
            row = {
                'year': year,
                'entries': [entries_lookup[(year.id, key.id)] for key in keys],
            }
            rows.append(row)

        followup_data_tables[level] = {
            'keys': keys,
            'rows': rows,
        }

    if request.method == "POST":
        for level_data in followup_data_tables.values():
            for row in level_data['rows']:
                for entry in row['entries']:
                    field_name = f"entry_{entry.id}"
                    val = request.POST.get(field_name)
                    try:
                        entry.value = int(val) if val else None
                        entry.save()
                    except ValueError:
                        pass  # Optionally handle invalid input


    #Disable fields for read-only version
    if readonly:
        for field in form.fields.values():
            field.disabled = True




    context = dict(selfstudy=selfstudy, school=school, standards=standards, active_sublink="student", active_link="profile",
                   form_id=form_id, grade_labels = grade_labels, valid_grades=valid_grades,
                   enrollment_by_grade_and_year=enrollment_by_grade_and_year,
                   previous_school_years=previous_school_years,
                   student_baptism_data=student_baptism_data,
                   student_data=student_data, international=international,
                   followup_data_tables = followup_data_tables,
                   total_by_year=total_by_year, total_baptism_data=total_baptism_data,
                   annual_report_id=annual_report.id,
                   percentage_non_sda_home=round(percentage_non_sda_home, 1),
                   percentage_baptized=round(percentage_baptized, 1),
                   projected_enrollment_form=form,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_student.html', context)


def get_grade_range_for_level(level_type):
    if level_type == 'elementary':
        return list(range(1, 9))  # Grades 1–8
    elif level_type == 'secondary':
        return list(range(9, 13))  # Grades 9–12
    return []

@login_required(login_url='login')
def profile_student_achievement(request, selfstudy_id, readonly=False):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_achievement"

#General Achievement data
    try:
        achievement = school_profile.achievement_data.get()
    except StudentAchievementData.DoesNotExist:
        achievement = StudentAchievementData(school_profile=school_profile)
        achievement.save()

    if readonly:
        extra_forms=0
    else:
        existing_tests = achievement.grade_level_tests.count()
        extra_forms = max(1, 5 - existing_tests)  # Always show at least one blank, up to 5 total

    GradeLevelTestFormSet = modelformset_factory(GradeLevelTest, form=GradeLevelTestForm, extra=extra_forms, can_delete=True)

    if request.method == 'POST':
        student_achievement_form = StudentAchievementDataForm(request.POST, instance=achievement)
        formset = GradeLevelTestFormSet(request.POST, queryset=achievement.grade_level_tests.all())

        if student_achievement_form.is_valid() and formset.is_valid():
            achievement = student_achievement_form.save(commit=False)
            achievement.school_profile = school_profile  # in case it was just created
            achievement.save()

            grade_tests = formset.save(commit=False)
            for test in grade_tests:
                test.achievement_data = achievement
                test.save()
    else:
        student_achievement_form = StudentAchievementDataForm(instance=achievement)
        formset = GradeLevelTestFormSet(queryset=achievement.grade_level_tests.all())


#Standardized test scores for the last three years
    level_types = school.get_school_type()
    if level_types:
        # Get the current school year from the accreditation model, # Extract the start year from the 'name' field, which is in the format "2024-2025"
        current_school_year = selfstudy.accreditation.school_year
        start_year = int(current_school_year.name.split('-')[0])
        # Generate the last 3 school year names (e.g., "2024-2025", "2023-2024", ...)
        school_year_names = [f"{start_year - i}-{start_year + 1 - i}" for i in range(3)]
        school_years = SchoolYear.objects.filter(name__in=school_year_names)
        school_years = school_years[::-1]  # Reverse the order of years to have the current year last

        # Prefetch related scores
        sessions = StandardizedTestSession.objects.filter(school=school, school_year__in=school_years).select_related(
            'school_year').prefetch_related('scores')

        # Create a dictionary to lookup scores by session_id, subject, and grade
        grouped_by_level = defaultdict(lambda: defaultdict(list))

        # Loop through each session and group them by school year and grade level
        for session in sessions:
            score_map = defaultdict(dict)
            for score in session.scores.all():
                score_map[score.subject][score.grade] = score.score

            session_data = {
                'session': session,
                'grade_range': get_grade_range_for_level(session.grade_level_type),
                'subjects': sorted(score_map.keys()),
                'scores': score_map
            }

            grouped_by_level[session.grade_level_type][session.school_year.name].append(session_data)

        # Simplify and serialize grouped_sessions data
        serialized_sessions = []
        for level_type, school_years_group in grouped_by_level.items():
            level_data = {
                'level_type': level_type,
                'school_years': []
            }
            for school_year, sessions in school_years_group.items():
                year_data = {
                    'school_year': school_year,
                    'sessions': []
                }
                for session_data in sessions:
                    session_info = {
                        'session_id':session_data['session'].id,
                        'test_type': session_data['session'].test_type,
                        'test_name': session_data['session'].test_name,
                        'grade_range': session_data['grade_range'],
                        'subjects': session_data['subjects'],
                        'scores': {subject: {grade: str(score) for grade, score in subject_scores.items()}
                                   for subject, subject_scores in session_data['scores'].items()}
                    }
                    year_data['sessions'].append(session_info)
                level_data['school_years'].append(year_data)
            serialized_sessions.append(level_data)

    else:
        school_years = sessions = grouped_by_level = serialized_sessions = None

    # Add this near your serialized_sessions generation
    existing_keys = set()
    for level in serialized_sessions:
        for year_data in level["school_years"]:
            if year_data["sessions"]:
                key = f"{level['level_type'].lower()}|{year_data['school_year']}"
                existing_keys.add(key)

    if readonly:
        for field in student_achievement_form.fields.values():
            field.disabled = True
        for subform in formset:
            for field in subform.fields.values():
                field.disabled = True

    context = dict(selfstudy=selfstudy, school=school, standards=standards, active_sublink="achievement", active_link="profile",
                   form_id=form_id,
                   level_types=level_types,
                   student_achievement_form = student_achievement_form,
                   grade_level_test_formset = formset,
                   sessions=sessions, grouped_by_level=grouped_by_level, serialized_sessions=serialized_sessions,
                   school_years=school_years,
                   existing_keys=existing_keys,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_student_achievement.html', context)


def manage_standardized_test_scores(request, school_id=None, school_year_name=None, level_type=None, session_id=None):

    if session_id:
        session = get_object_or_404(StandardizedTestSession, id=session_id)
        school = session.school
        school_year = session.school_year
        level_type = session.grade_level_type
    else:
        school = get_object_or_404(School, id=school_id)
        school_year = get_object_or_404(SchoolYear, name=school_year_name)
        session = None  # will create later if needed

    next_url = request.GET.get('next')

    # Determine grade range
    grade_range = range(1, 9) if level_type == "elementary" else range(9, 13)

    # Create session only if it doesn't exist yet
    if not session:
        session = StandardizedTestSession(
            school=school, school_year=school_year, grade_level_type=level_type,
            test_type="OT"  # default; you can adjust or prompt user to fill this
        )

    SUBJECTS = ['ENGLISH', 'READING', 'WRITING', 'MATH', 'SCIENCE', 'SOCIAL STUDIES', 'COMPOSITE']
    form_dict = {}

    if request.method == 'POST':
        session_form = StandardizedTestSessionForm(request.POST, instance=session)
        is_valid = session_form.is_valid()

        for subject in SUBJECTS:
            form_dict[subject] = {}
            for grade in grade_range:
                prefix = f"{subject}_{grade}"
                if session_id:
                    try:
                        score = StandardizedTestScore.objects.get(session=session, subject=subject, grade=grade)
                    except StandardizedTestScore.DoesNotExist:
                        score = StandardizedTestScore(session=session, subject=subject, grade=grade)
                else:
                    score = StandardizedTestScore(session=session, subject=subject, grade=grade)
                form = StandardizedTestScoreForm(request.POST, instance=score, prefix=prefix)
                form_dict[subject][grade] = form
                if form.has_changed():
                    is_valid = is_valid and form.is_valid()

        if is_valid:
            session_form.save()
            for subject_forms in form_dict.values():
                for form in subject_forms.values():
                    if form.has_changed() and form.is_valid():
                        score = form.save(commit=False)
                        if score.score is not None:
                            score.session = session
                            score.save()
            messages.success(request, "Scores updated successfully.")
            return redirect(next_url)

    else:
        session_form = StandardizedTestSessionForm(instance=session)
        for subject in SUBJECTS:
            form_dict[subject] = {}
            for grade in grade_range:
                if session_id:
                    try:
                        score = StandardizedTestScore.objects.get(session=session, subject=subject, grade=grade)
                    except StandardizedTestScore.DoesNotExist:
                        score = StandardizedTestScore(subject=subject, grade=grade)
                else:
                    score = StandardizedTestScore(session=session, subject=subject, grade=grade)
                form = StandardizedTestScoreForm(instance=score, prefix=f"{subject}_{grade}")
                form_dict[subject][grade] = form

    context = dict( session=session, session_form=session_form, form_dict=form_dict,
        school=school, school_year=school_year,
        level_type=level_type, grade_range=grade_range,)

    return render(request, 'selfstudy/add_standardized_test_scores.html', context)


@login_required(login_url='login')
def profile_secondary_curriculum(request, selfstudy_id, readonly=False):
    """Main personnel profile view, handling personnel data and FTE data."""
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_curriculum"

    teachers = SelfStudyPersonnelData.objects.filter(school_profile=school_profile)
    teacher_names = [f"{t.first_name} {t.last_name}".strip() for t in teachers if t.first_name or t.last_name]

    other_curriculum, _ = OtherCurriculumData.objects.get_or_create(school_profile=school_profile)

    categories = CourseCategory.objects.all()
    context = dict(selfstudy=selfstudy, school=school, standards=standards, active_sublink="curriculum", active_link="profile",
                   form_id=form_id, category_formsets=[], other_curriculum = other_curriculum,
                   teacher_names=teacher_names,
                   readonly=readonly)

    if request.method == 'POST':
        all_valid = True
        formsets_by_category = []
        other_form = OtherCurriculumDataForm(request.POST, instance=other_curriculum)

        # Loop through categories and process the formsets
        for category in categories:
            prefix = f'cat_{category.id}'
            FormSet = modelformset_factory(
                SecondaryCurriculumCourse,
                form=SecondaryCurriculumCourseForm,
                extra=1,
                can_delete=False
            )
            queryset = SecondaryCurriculumCourse.objects.filter(school_profile=school_profile, category=category)
            formset = FormSet(request.POST, queryset=queryset, prefix=prefix)

            if formset.is_valid():
                formsets_by_category.append((category, formset))
            else:
                all_valid = False

            # Always append the formset (valid or invalid) to the context
            context['category_formsets'].append((category, formset))

        context['other_form'] = other_form

        # If all formsets are valid, save the data
        if all_valid:
            for category, formset in formsets_by_category:
                instances = formset.save(commit=False)

                for obj in formset.deleted_objects:
                    obj.delete()

                for instance in instances:
                    instance.school_profile = school_profile
                    instance.category = category
                    instance.save()

            other_form.save()
            return redirect(request.path)  # Redirect to the same page or to a success page

    else:  # For GET request, render the initial formsets
        for category in categories:
            prefix = f'cat_{category.id}'

            if readonly: extra_forms=0
            else: extra_forms=3

            FormSet = modelformset_factory(
                SecondaryCurriculumCourse,
                form=SecondaryCurriculumCourseForm,
                extra=extra_forms,
                can_delete=False
            )
            queryset = SecondaryCurriculumCourse.objects.filter(school_profile=school_profile, category=category)
            formset = FormSet(queryset=queryset, prefix=prefix)
            if readonly:
                for subform in formset:
                    for field in subform.fields.values():
                        field.disabled=True
            context['category_formsets'].append((category, formset))

        other_form = OtherCurriculumDataForm(instance=other_curriculum)
        if readonly:
            for field in other_form.fields.values():
                field.disabled = True
        context['other_form'] = other_form

    # Render the template with the appropriate context (now always contains formsets)
    return render(request, 'selfstudy/profile_secondary_curriculum.html', context)



@login_required(login_url='login')
def profile_support_services(request, selfstudy_id, readonly=False):
    """Main personnel profile view, handling personnel data and FTE data."""
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_services"

    # Try to get an existing SupportService for the school profile, or create a new one
    support_service, created = SupportService.objects.get_or_create(school_profile=school_profile)

    if request.method == 'POST':
        form = SupportServiceForm(request.POST, instance=support_service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Support service details updated successfully.')

    else:
        form = SupportServiceForm(instance=support_service)

    if readonly:
        for field in form.fields.values():
            field.disabled = True


    context = dict(selfstudy=selfstudy, school=school, standards=standards, active_sublink="services", active_link="profile",
                   form_id=form_id, form=form,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_support_services.html', context)


@login_required(login_url='login')
def profile_philanthropy(request, selfstudy_id, readonly=False):
    """Main personnel profile view, handling personnel data and FTE data."""
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    school = selfstudy.accreditation.school
    standards = Standard.objects.top_level()
    form_id = f"{selfstudy.id}_philantrophy"

    philanthropy, created = PhilantrophyProgram.objects.get_or_create(school_profile=school_profile)

    if request.method == 'POST':
        form = PhilantrophyProgramForm(request.POST, instance=philanthropy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Support service details updated successfully.')

    else:
        form = PhilantrophyProgramForm(instance=philanthropy)

    if readonly:
        for field in form.fields.values():
            field.disabled = True

    context = dict(selfstudy=selfstudy, school=school, standards=standards, active_sublink="philanthropy", active_link="profile",
                   form_id=form_id, form=form,
                   readonly=readonly)

    return render(request, 'selfstudy/profile_philanthropy.html', context)