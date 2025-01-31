from dis import Instruction

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from users.utils import is_in_any_group
from django.contrib import messages

from django.db.models import Max
from django.contrib.auth.models import Group
from django.utils import timezone

from users.utils import is_in_any_group
from users.models import UserProfile
from .forms import *
from accreditation.models import Standard, Indicator, Level
from apr.models import APR, ActionPlan
from reporting.models import AnnualReport, Personnel, StaffStatus
from .models import *

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

    # Create entries for FinancialTwoYearDataEntries for all keys
    for data_key in FinancialTwoYearDataKey.objects.filter(active=True):
        FinancialTwoYearDataEntry.objects.get_or_create(
            school_profile=school_profile,
            data_key=data_key,
        )
    # Create entries for FinancialAdditionalDataEntries for all keys
    for data_key in FinancialAdditionalDataKey.objects.filter(active=True):
        FinancialAdditionalDataEntry.objects.get_or_create(
            school_profile=school_profile,
            data_key=data_key,
        )

def setup_indicator_evaluations(selfstudy):
    """
    Creates IndicatorEvaluation objects for all active Indicators associated with
    the SelfStudy's accreditation standards, in bulk. Ensures no duplicates are created.
    """
    # Fetch all active indicators with their associated standards
    indicators = Indicator.objects.filter(active=True).select_related('standard')

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
        if created:
            print(standard)

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
            print("POST")
            if "submit_selfstudy" in request.POST:
                selfstudy.submission_date = timezone.now().date()
                print("submit")
            elif "reopen_selfstudy" in request.POST:
                selfstudy.submission_date = None
                print("reopen")
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

def selfstudy_standard(request, selfstudy_id, standard_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards = Standard.objects.top_level()
    standard = get_object_or_404(Standard, id=standard_id, parent_standard__isnull=True)

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
            # Group levels for each indicator
            levels_dict = {
                indicator.id: Level.objects.filter(indicator=indicator).order_by("-level")
                for indicator in indicators
            }
            grouped_data.append({
                "standard": substandard,
                "indicators": indicators,
                "evaluations": evaluations,
                "levels_dict": levels_dict,
            })
        # Evidence is specific to the main standard
    else:
        substandards_exist=False
        evaluations = IndicatorEvaluation.objects.filter(selfstudy=selfstudy, standard=standard)
        indicators = Indicator.objects.filter(standard=standard, active=True)
        levels_dict = {
            indicator.id: Level.objects.filter(indicator=indicator).order_by("-level")
            for indicator in indicators
        }
        grouped_data.append({
            "standard": standard,
            "indicators": indicators,
            "evaluations": evaluations,
            "levels_dict": levels_dict,
        })

    if request.method == "POST":
        formset = IndicatorEvaluationFormSet(request.POST, queryset=IndicatorEvaluation.objects.filter(
            selfstudy=selfstudy, standard__in=[standard] + list(substandards) ))
        standard_form = StandardEvaluationForm(request.POST, instance=standard_evaluation)
        if formset.is_valid() and standard_form.is_valid():
            formset.save()
            standard_form.save()
            # Redirect to the next standard or a completion page
            #return redirect('selfstudy:completion')  # Or another standard
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

    context = dict(selfstudy=selfstudy, standards = standards, standard=standard,
                   formset = formset, standard_form=standard_form,
                   active_link=standard_id, evidence_list=evidence_list, narrative=narrative,
                   grouped_data = grouped_data, substandards_exist=substandards_exist)

    return render(request, 'selfstudy/standard.html', context)

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

def selfstudy_actionplan(request, accreditation_id, action_plan_id=None):
    accreditation = get_object_or_404(Accreditation, id=accreditation_id)

    selfstudy = get_object_or_404(SelfStudy, accreditation=accreditation)
    standards= Standard.objects.top_level()
    actionplans = ActionPlan.objects.filter(accreditation=accreditation).order_by('number')

    # Get the ActionPlan if updating, otherwise create a new one
    if action_plan_id:
        action_plan = get_object_or_404(ActionPlan, id=action_plan_id, accreditation=accreditation)
    else:
        action_plan = ActionPlan(accreditation=accreditation)

    if request.method == 'POST':
        if 'delete' in request.POST and action_plan.id:
            print("delete",action_plan)
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
        formset = ActionPlanStepsFormSet(instance=action_plan)

    context = dict(ap_form=ap_form, formset=formset, action_plan=action_plan, accreditation_id=accreditation_id,
                   selfstudy=selfstudy,standards=standards,
                   active_link=action_plan.id, actionplans=actionplans)

    return render(request, 'selfstudy/action_plan.html', context)

def selfstudy_coordinating_team(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards= Standard.objects.top_level()

    if is_in_any_group(request.user, ['staff','principal','registrar']):
        privileges=True
    else:
        privileges=False

    teams = SelfStudy_Team.objects.filter(selfstudy=selfstudy)

    context=dict(selfstudy=selfstudy, standards=standards, active_link="coordinating_team",
                 teams=teams, privileges=privileges)
    return render(request, 'selfstudy/coordinating_team.html', context)

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
                   personnel_without_users=personnel_without_users,
                   inactive_users =inactive_users,)

    return render(request, 'selfstudy/add_coordinating_team_members.html', context)

def selfstudy_profile(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards = Standard.objects.top_level()

    #TODO Add General Information Here

    context = dict(selfstudy=selfstudy, standards = standards,
                   active_link="profile",
                   )
    return render(request, 'selfstudy/profile.html', context)

def profile_history(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()

    history_form = SchoolHistoryForm(instance=school_profile)

    if request.method == 'POST':
        history_form = SchoolHistoryForm(request.POST, instance=school_profile)
        if history_form.is_valid():
            history_form.save()
            messages.success(request, "School history has been successfully saved!")
        else:
            messages.error(request,"School history was not saved!")

    context = dict(selfstudy=selfstudy, standards = standards,
                   history_form = history_form,
                   active_sublink="history",
                   )

    return render(request, 'selfstudy/profile_history.html', context)

def profile_financial_data(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()

    # Query related financial data entries
    two_year_data_queryset = FinancialTwoYearDataEntry.objects.filter(school_profile=school_profile)
    additional_data_queryset = FinancialAdditionalDataEntry.objects.filter(school_profile=school_profile)


    if request.method == 'POST':
        two_year_formset = FinancialTwoYearDataFormSet(request.POST or None, queryset=two_year_data_queryset, prefix="two_years")
        additional_formset = FinancialAdditionalDataFormSet(request.POST or None, queryset=additional_data_queryset, prefix="additional")

        if two_year_formset.is_valid():
            two_year_formset.save()
            messages.success(request, "2-Year Financial Data has been successfully saved!")
        else:
            messages.error(request, "Some 2-year Financial Data was not saved!")

        if additional_formset.is_valid():
            additional_formset.save()
            messages.success(request, "Additional Financial Data has been successfully saved!")
        else:
            messages.error(request, "Some Additional Financial Data was not saved!")

    # Initialize formsets
    two_year_formset = FinancialTwoYearDataFormSet(queryset=two_year_data_queryset, prefix="two_years")
    additional_formset = FinancialAdditionalDataFormSet(queryset=additional_data_queryset, prefix="additional")

    context = dict(selfstudy=selfstudy, standards = standards,active_link="profile",
                    two_year_formset = two_year_formset, additional_formset = additional_formset )

    return render(request, 'selfstudy/profile_financial_data.html', context)