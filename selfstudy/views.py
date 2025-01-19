from django.shortcuts import render, get_object_or_404, redirect

from datetime import datetime

from .models import *
from .forms import *
from accreditation.models import Standard, Indicator, Level

#Creating the self-study views
def get_or_create_selfstudy(accreditation):
    selfstudy, created = SelfStudy.objects.get_or_create(
        accreditation=accreditation,
    )
    return selfstudy

def setup_coordinating_team_and_members(selfstudy, standards):
    #Ensures a CoordinatingTeam exists for the given SelfStudy, and creates TeamMember objects for all Standards if they don't already exist.
    # Check if a CoordinatingTeam object exists for this SelfStudy
    coordinating_team, created = CoordinatingTeam.objects.get_or_create(selfstudy=selfstudy)
    # Create TeamMember objects for each Standard
    for standard in standards:
        # Check if the TeamMember already exists
        if not TeamMember.objects.filter(coordinating_team=coordinating_team, standard=standard).exists():
            # Create a TeamMember object only if it doesn't already exist
            TeamMember.objects.create(
                coordinating_team=coordinating_team,
                standard=standard,
            )

def setup_school_profile(selfstudy):
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)

    # Create entries for FinancialTwoYearDataEntries for all keys
    for key in FinancialTwoYearDataKey.objects.all():
        FinancialTwoYearDataEntries.objects.get_or_create(
            school_profile=school_profile,
            key=key,
        )
    # Create entries for FinancialAdditionalDataEntries for all keys
    for key in FinancialAdditionalDataKey.objects.all():
        FinancialAdditionalDataEntries.objects.get_or_create(
            school_profile=school_profile,
            key=key,
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
            score=None,  reference_documents=[], explanation='',
        )
        for indicator in new_indicators
    ]

    indicator_evaluations.sort(key=lambda x: x.indicator.code) # Sort the evaluations by indicator code (if needed)
    IndicatorEvaluation.objects.bulk_create(indicator_evaluations) # Bulk create the new evaluations

    #return len(indicator_evaluations)  # Optionally return the count of created objects

def setup_standard_evaluation(selfstudy, standards):
    # Create StandardEvaluation objects for the selfstudy
    for standard in standards:
        StandardEvaluation.objects.get_or_create(selfstudy=selfstudy,standard=standard,)


def setup_selfstudy(request, accreditation_id):
    # Retrieve the Accreditation object by ID
    accreditation = get_object_or_404(Accreditation, id=accreditation_id)
    selfstudy = get_or_create_selfstudy(accreditation)

    standards = Standard.objects.top_level()

    setup_coordinating_team_and_members(selfstudy, standards)
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

        context = dict(selfstudy=selfstudy, standards=standards)
        return render(request, 'selfstudy/selfstudy.html', context)

    except SelfStudy.DoesNotExist:
        # If no SelfStudy is found, redirect to setup_selfstudy
        accreditation = get_object_or_404(Accreditation, id=selfstudy_id)  # Assuming the selfstudy_id matches accreditation_id
        return setup_selfstudy(request, accreditation_id=accreditation.id)

#School filling out the self study views

def selfstudy_profile(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    school_profile, created = SchoolProfile.objects.get_or_create(selfstudy=selfstudy)
    standards = Standard.objects.top_level()

    # Query related financial data entries
    two_year_data_queryset = FinancialTwoYearDataEntries.objects.filter(school_profile=school_profile)
    additional_data_queryset = FinancialAdditionalDataEntries.objects.filter(school_profile=school_profile)

    # Initialize formsets
    two_year_formset = FinancialTwoYearDataFormSet(queryset=two_year_data_queryset)
    additional_formset = FinancialAdditionalDataFormSet(queryset=additional_data_queryset)

    profile_form = SchoolProfileForm(instance=school_profile)

    if request.method == 'POST':
        profile_form = SchoolProfileForm(request.POST, instance=school_profile)
        two_year_formset = FinancialTwoYearDataFormSet(request.POST, queryset=two_year_data_queryset)
        additional_formset = FinancialAdditionalDataFormSet(request.POST, queryset=additional_data_queryset)

        if profile_form.is_valid():
            profile_form.save()

        if two_year_formset.is_valid() and additional_formset.is_valid():
            two_year_formset.save()
            additional_formset.save()
        else:
            print(two_year_formset.errors)
            print(additional_formset.errors)

    context = dict(selfstudy=selfstudy, standards = standards,
                   profile_form = profile_form,
                    two_year_formset = two_year_formset, additional_formset = additional_formset, #financial data forms
                   active_link="profile",
                   )

    return render(request, 'selfstudy/profile.html', context)



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
        else:
            error_message = "There were some errors with your submission. Please review the form and try again."
            # Add the error message to the context to display in the template
            context = dict(selfstudy=selfstudy, standards = standards, standard=standard,
                           active_link=standard_id, evidence_list=evidence_list, narrative=narrative,
                           formset = formset, standard_form=standard_form,
                           grouped_data = grouped_data, substandards_exist=substandards_exist,
                           error_message=error_message)

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

