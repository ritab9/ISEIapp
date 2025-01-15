from django.shortcuts import render, get_object_or_404, redirect

from datetime import datetime

from .models import *
from .forms import *

#Creating the self-study views
def get_or_create_selfstudy(accreditation):
    """
    Helper function to get or create a SelfStudy object for a given Accreditation.
    """
    selfstudy, created = SelfStudy.objects.get_or_create(
        accreditation=accreditation,
        defaults={'last_updated': datetime.now()}
    )
    return selfstudy

def setup_coordinating_team_and_members(selfstudy):
    """
    Ensures a CoordinatingTeam exists for the given SelfStudy, and creates TeamMember objects for all Standards if they don't already exist.
    """
    # Check if a CoordinatingTeam object exists for this SelfStudy
    coordinating_team, created = CoordinatingTeam.objects.get_or_create(selfstudy=selfstudy)

    # Create TeamMember objects for each Standard
    standards = Standard.objects.top_level()
    for standard in standards:
        # Check if the TeamMember already exists
        if not TeamMember.objects.filter(coordinating_team=coordinating_team, standard=standard).exists():
            # Create a TeamMember object only if it doesn't already exist
            TeamMember.objects.create(
                coordinating_team=coordinating_team,
                standard=standard,
            )

def setup_school_profile(selfstudy):
    """
    Ensures a SchoolProfile exists for the given SelfStudy.
    Initializes financial data fields with keys if they are empty.
    """
    # Check if a SchoolProfile object exists for this SelfStudy
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)

    # Initialize financial_2year_data if empty
    if not school_profile.financial_2year_data:
        financial_2year_data = {
            key.name: {"two_years_ago": None, "one_year_ago": None}
            for key in FinancialTwoYearDataKey.objects.all()
        }
        school_profile.financial_2year_data = financial_2year_data

    # Initialize financial_additional_data if empty
    if not school_profile.financial_additional_data:
        financial_additional_data = {
            key.name: None for key in FinancialAdditionalDataKey.objects.all()
        }
        school_profile.financial_additional_data = financial_additional_data

    # Save the SchoolProfile after populating the fields
    school_profile.save()

def setup_indicator_evaluations(selfstudy):
    """
    Creates IndicatorEvaluation objects for all active Indicators in the standards
    associated with the SelfStudy's Accreditation, in bulk.
    """
    # Fetch active indicators and their associated standards
    indicators = Indicator.objects.filter(active=True).select_related('standard')

    # Prepare a list to hold IndicatorEvaluation objects
    indicator_evaluations = []

    # Iterate over each indicator and create an IndicatorEvaluation object
    for indicator in indicators:
        indicator_evaluations.append(
            IndicatorEvaluation(
                selfstudy=selfstudy,
                indicator=indicator,
                standard=indicator.standard,
                score=None,  # Placeholder until school provides data
                reference_documents='',
                explanation='',
            )
        )

    # Use bulk_create to insert all the evaluations in a single query
    if indicator_evaluations:
        indicator_evaluations.sort(key=lambda x: x.indicator.code)
        IndicatorEvaluation.objects.bulk_create(indicator_evaluations)



def setup_selfstudy(request, accreditation_id):
    # Retrieve the Accreditation object by ID
    accreditation = get_object_or_404(Accreditation, id=accreditation_id)
    selfstudy = SelfStudy.objects.filter(accreditation=accreditation).first()

    #get_or_create_selfstudy(accreditation)

    #setup_coordinating_team_and_members(selfstudy)
    #setup_school_profile(selfstudy)
    #setup_indicator_evaluations(selfstudy)

    standards = Standard.objects.top_level()

    context = dict(selfstudy=selfstudy, standards=standards)

    return render(request, 'selfstudy/setup_selfstudy.html', context)


#School filling out the self study views

def selfstudy_profile(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()

    if request.method == 'POST':
        form = SchoolProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('selfstudy:completion')  # Or redirect to another tab/section
    else:
        form = SchoolProfileForm(instance=profile)

    context = dict(selfstudy=selfstudy, form = form, standards = standards )

    return render(request, 'selfstudy/profile.html', context)

def selfstudy_standard(request, selfstudy_id, standard_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards = Standard.objects.top_level()
    standard = get_object_or_404(Standard, id=standard_id, parent_standard__isnull=True)

    evaluations = IndicatorEvaluation.objects.filter(selfstudy=selfstudy, standard=standard)

    if request.method == 'POST':
        formset = IndicatorEvaluationFormSet(request.POST, queryset=evaluations)
        if formset.is_valid():
            formset.save()
            # Redirect to the next standard or a completion page
            return redirect('selfstudy:completion')  # Or another standard
    else:
        formset = IndicatorEvaluationFormSet(queryset=evaluations)

    context = dict(selfstudy=selfstudy, standards = standards, standard=standard, formset = formset)

    return render(request, 'selfstudy/standard.html', context)

