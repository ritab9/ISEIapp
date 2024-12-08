from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users

from apr.models import *
from .forms import PriorityDirectiveFormSet, DirectiveFormSet, RecommendationFormSet,ActionPlanForm, ActionPlanStepsFormSet
from accreditation.models import Accreditation

from django.db.models import Max, Q
from collections import defaultdict, OrderedDict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



#ISEI views for managing APRs - creating and updating if needed

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def manage_apr(request, accreditation_id):
    # Find the related Accreditation and School object
    accreditation = Accreditation.objects.get(pk=accreditation_id)

    if not hasattr(accreditation, 'apr'):
        # Create APR object
        apr = APR(accreditation=accreditation)
        apr.save()
        # Create APRSchoolYear objects
        year_start = accreditation.term_start_date.year
        year_end = accreditation.term_end_date.year

        for year in range(year_start, year_end):
            apr_school_year = APRSchoolYear(name=f'{year}-{year + 1}', apr=apr)
            apr_school_year.save()
    else:
        apr = accreditation.apr

    priority_directives = PriorityDirective.objects.filter(apr=apr)
    directives = Directive.objects.filter(apr=apr)
    recommendations = Recommendation.objects.filter(apr=apr)
    action_plans = ActionPlan.objects.filter(apr=apr)

    action_plans_with_steps = []
    for action_plan in action_plans:
        steps = ActionPlanSteps.objects.filter(action_plan=action_plan)
        action_plans_with_steps.append((action_plan, steps))

    context = {
        'apr': apr,
        'priority_directives': priority_directives,
        'directives': directives,
        'recommendations': recommendations,
        'action_plans_with_steps': action_plans_with_steps
    }

    return render(request, 'apr/manage_apr.html', context)

#a general function to handle Priority Directives, Directives and Recommendations formsets
def handle_formset(request, apr_id, model, formset_class, form_action_url):
    apr = APR.objects.get(id=apr_id)

    # Use the formset class passed in as a parameter
    if request.method == 'POST':
        formset = formset_class(request.POST)

        if formset.is_valid():
            # Assign the apr to each object before saving
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    if instance.description:  # Only save if description is provided
                        instance.apr = apr  # Assign the apr to the object
                        instance.save()  # Now save the object
                    else:
                        instance.delete()
            create_progress_records(apr)
            # Redirect after saving
            return redirect('manage_apr', apr.accreditation.id)
    else:
        # Use existing objects for the apr
        formset = formset_class(queryset=model.objects.filter(apr=apr))

    context = dict(apr=apr, formset=formset, model_name=model.__name__, form_action_url = form_action_url)
    # Render the template with the formset
    return render(request, 'apr/handle_formset.html', context)

#view for adding priority_directives
def add_priority_directives(request, apr_id):
    return handle_formset(
        request, apr_id, PriorityDirective, PriorityDirectiveFormSet, form_action_url=f"/apr/{apr_id}/add_priority_directives/"
    )

# View for adding Directives
def add_directives(request, apr_id):
    return handle_formset(
        request, apr_id, Directive, DirectiveFormSet, form_action_url=f"/apr/{apr_id}/add_directives/"
    )

# View for adding Recommendations
def add_recommendations(request, apr_id):
    return handle_formset(
        request, apr_id, Recommendation, RecommendationFormSet, form_action_url=f"/apr/{apr_id}/add_recommendations/"
    )

def manage_action_plan(request, apr_id, action_plan_id=None):
    apr = get_object_or_404(APR, id=apr_id)

    # Get the ActionPlan if updating, otherwise create a new one
    if action_plan_id:
        action_plan = get_object_or_404(ActionPlan, id=action_plan_id, apr=apr)
    else:
        action_plan = ActionPlan(apr=apr)

    if request.method == 'POST':
        form = ActionPlanForm(request.POST, instance=action_plan)
        formset = ActionPlanStepsFormSet(request.POST, instance=action_plan)

        if form.is_valid():
            action_plan = form.save()
            if formset.is_valid():
                existing_steps = ActionPlanSteps.objects.filter(action_plan=action_plan)
                max_number = existing_steps.aggregate(Max('number'))['number__max'] or 0

                steps = formset.save(commit=False)
                for i, step in enumerate(steps, start=max_number + 1):
                    step.number = i
                    step.action_plan = action_plan  # Link the step to the ActionPlan
                    step.save()

                #This might be needed if existing steps need renumbering
                #for i, step in enumerate(existing_steps, start=1):
                #    step.number = i
                #    step.save()

            return redirect('manage_apr', apr.accreditation.id)  # Redirect to APR detail page

    else:
        form = ActionPlanForm(instance=action_plan)
        formset = ActionPlanStepsFormSet(instance=action_plan)

    context = {
        'form': form,
        'formset': formset,
        'apr': apr,
        'action_plan': action_plan,
    }
    return render(request, 'apr/manage_action_plan.html', context)

#create the records to tag progress per school year
def create_progress_records(apr):
    for apr_school_year in apr.aprschoolyear.all():
        for priority_directive in apr.prioritydirective_set.all():
            Progress.objects.get_or_create(
                school_year=apr_school_year,
                priority_directive=priority_directive
            )
        for directive in apr.directive_set.all():
            Progress.objects.get_or_create(
                school_year=apr_school_year,
                directive=directive
            )
        for recommendation in apr.recommendation_set.all():
            Progress.objects.get_or_create(
                school_year=apr_school_year,
                recommendation=recommendation
            )
        for action_plan in apr.actionplan_set.all():
            Progress.objects.get_or_create(
                school_year=apr_school_year,
                action_plan=action_plan,
            )




#School views for tracking APR progress
def apr_progress_report(request, apr_id):
    apr = get_object_or_404(APR, id=apr_id)

    # Fetch all directives, recommendations, and action plans related to the APR
    priority_directives = PriorityDirective.objects.filter(apr=apr).order_by('number')
    directives = Directive.objects.filter(apr=apr).order_by('number')
    recommendations = Recommendation.objects.filter(apr=apr).order_by('-number')
    action_plans = ActionPlan.objects.filter(apr=apr).order_by('-number')

    school_years = APRSchoolYear.objects.filter(apr=apr).order_by('name')

    # Create empty defaultdictionaries of dicts for grouping progress per directive type
    priority_directives_progress = defaultdict(dict)
    directives_progress = defaultdict(dict)
    recommendations_progress = defaultdict(dict)
    action_plans_progress = defaultdict(dict)

    # Create individual querysets for each progress object related to Priority Directives, Directives,
    # Recommendations and Action Plans
    priority_progress = Progress.objects.filter(priority_directive__in=priority_directives).order_by(
        'school_year__name')
    directive_progress = Progress.objects.filter(directive__in=directives).order_by('school_year__name')
    recommendation_progress = Progress.objects.filter(recommendation__in=recommendations).order_by('school_year__name')
    action_plan_progress = Progress.objects.filter(action_plan__in=action_plans).order_by('school_year__name')

    for progress in priority_progress:
        directive_key = f"{progress.priority_directive.number}. {progress.priority_directive.description}"
        priority_directives_progress[directive_key].setdefault(progress.school_year, []).append(progress)

    for progress in directive_progress:
        directive_key = f"{progress.directive.number}. {progress.directive.description}"
        directives_progress[directive_key].setdefault(progress.school_year, []).append(progress)

    for progress in recommendation_progress:
        directive_key = f"{progress.recommendation.number}. {progress.recommendation.description}"
        recommendations_progress[directive_key].setdefault(progress.school_year, []).append(progress)

    for progress in action_plan_progress:
        directive_key = f"{progress.action_plan.number}. {progress.action_plan.objective}"
        action_plans_progress[directive_key].setdefault(progress.school_year, []).append(progress)

    # convert to dictionary from defaultdict
    priority_directives_progress = dict(priority_directives_progress)
    directives_progress = dict(directives_progress)
    recommendations_progress = dict(recommendations_progress)
    action_plans_progress = dict(action_plans_progress)

    return render(request, 'apr/apr_progress_reportB.html', {
    #return render(request, 'apr/apr_progress_report.html', {
        'apr': apr,
        'school_years': school_years,
        'priority_directives_progress': priority_directives_progress,
        'directives_progress': directives_progress,
        'recommendations_progress': recommendations_progress,
        'action_plans_progress': action_plans_progress,
    })



@csrf_exempt  # Use this temporarily for testing
def update_progress(request, progress_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the incoming JSON data
            description = data.get('description', '')  # Get the 'description' field

            progress = get_object_or_404(Progress, id=progress_id)  # Retrieve the Progress object
            progress.description = description  # Update the description
            progress.save()  # Save the changes

            return JsonResponse({'description': progress.description})  # Respond with the updated description
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
