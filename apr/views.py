from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users

from apr.models import *
from .forms import *
from accreditation.models import Accreditation

from django.db.models import Max, Q
from collections import defaultdict, OrderedDict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
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
    else:
        apr = accreditation.apr

    year_start = accreditation.term_start_date.year
    year_end = accreditation.term_end_date.year

    # Create APRSchoolYear objects
    for year in range(year_start, year_end):
        apr_school_year, created = APRSchoolYear.objects.get_or_create(
            name=f'{year}-{year + 1}',
            apr=apr
        )

    apr_school_year, created = APRSchoolYear.objects.get_or_create(
        name=f'{year_start}-{year_end}',
        apr=apr,
        recommendation=True
    )

    action_plan_directives = ActionPlanDirective.objects.filter(apr=apr).order_by('number')
    priority_directives = PriorityDirective.objects.filter(apr=apr).order_by('number')
    directives = Directive.objects.filter(apr=apr).order_by('number')
    recommendations = Recommendation.objects.filter(apr=apr).order_by('number')
    action_plans = ActionPlan.objects.filter(apr=apr).order_by('number')

    action_plans_with_steps = []
    for action_plan in action_plans:
        steps = ActionPlanSteps.objects.filter(action_plan=action_plan).order_by('number')
        action_plans_with_steps.append((action_plan, steps))

    context = {
        'apr': apr,
        'action_plan_directives': action_plan_directives,
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
            create_progress_records(apr, model)
            # Redirect after saving
            return redirect('manage_apr', apr.accreditation.id)
    else:
        # Use existing objects for the apr
        formset = formset_class(queryset=model.objects.filter(apr=apr))

    context = dict(apr=apr, formset=formset, model_name=model.__name__, form_action_url = form_action_url)
    # Render the template with the formset
    return render(request, 'apr/handle_formset.html', context)

#view for adding priority_directives
def add_action_plan_directives(request, apr_id):
    return handle_formset(
        request, apr_id, ActionPlanDirective, ActionPlanDirectiveFormSet, form_action_url=f"/apr/{apr_id}/add_action_plan_directives/"
    )

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
                    if step.number is None:  # Only assign number if it doesn't already have one
                        step.number = i
                    step.action_plan = action_plan  # Link the step to the ActionPlan
                    step.save()

                #This might be needed if existing steps need renumbering
                #for i, step in enumerate(existing_steps, start=1):
                #    step.number = i
                #    step.save()
                create_progress_records(apr, ActionPlan)

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
def create_progress_records(apr, model):
    model_name = model.__name__

    if model_name == 'Recommendation':
        apr_school_year = APRSchoolYear.objects.get(apr=apr, recommendation=True)
        for recommendation in apr.recommendation_set.all():
            Progress.objects.get_or_create(
                school_year=apr_school_year,
                recommendation=recommendation
            )
    else:
        apr_school_years = APRSchoolYear.objects.filter(apr=apr, recommendation=False)
        for apr_school_year in apr_school_years:
            if model_name == 'PriorityDirective':
                for priority_directive in apr.prioritydirective_set.all():
                    Progress.objects.get_or_create(
                        school_year=apr_school_year,
                        priority_directive=priority_directive
                    )
            elif model_name == 'Directive':
                for directive in apr.directive_set.all():
                    Progress.objects.get_or_create(
                        school_year=apr_school_year,
                        directive=directive
                    )
            elif model_name == 'ActionPlan':
                for action_plan in apr.actionplan_set.all():
                    Progress.objects.get_or_create(
                        school_year=apr_school_year,
                        action_plan=action_plan,
                    )


#School views for tracking APR progress

#Grouping progress object in a dictionary by Priority Directive, Directive, Recommendation or Action Plan
def group_progress_by_directive(progress_queryset, directive_attr, include_steps=False):
    """
    Groups progress items by directive (using `directive_attr`) and school year.
    Args:
        progress_queryset: Queryset of Progress objects.
        directive_attr: Name of the attribute linking Progress to the directive type.
    Returns:
        defaultdict of dict: Nested dictionary grouped by directive and school year.
    """
    grouped_progress = defaultdict(lambda: {"progress": defaultdict(list), "steps": []})

    for progress in progress_queryset:
        directive = getattr(progress, directive_attr)  # Access dynamic directive field
        directive_number = directive.number
        directive_description = getattr(directive, 'description', None) or getattr(directive, 'objective', '')
        #progress_status = getattr(directive, 'progress_status', None)
        #directive_key = f"{directive_number}. {directive_description}"

        # Include ActionPlanSteps if requested
        if include_steps and directive_attr == 'action_plan':
            if not grouped_progress[directive]["steps"]:  # Avoid duplicates
                steps = list(directive.actionplansteps_set.all().order_by('number').values(
                    'number', 'person_responsible', 'action_steps', 'start_date', 'completion_date', 'resources'
                ))
                grouped_progress[directive]["steps"] = steps

        # Group progress by school year
        grouped_progress[directive]["progress"][progress.school_year].append(progress)

    # Sort progresses by school_year within each directive
    grouped_progress = {
        directive: {
            "steps": data["steps"],
            "progress": {
                school_year: sorted(progress_objs, key=lambda x: x.school_year.name)
                for school_year, progress_objs in sorted(data["progress"].items(), key=lambda x: x[0].name)
            },
        }
        for directive, data in grouped_progress.items()
    }

    # And then sort directives by their number:
    sorted_grouped_progress = dict(
        sorted(
            grouped_progress.items(),
            key=lambda item: item[0].number  # Extract and sort by the directive number
        )
    )


    return sorted_grouped_progress


def apr_progress_report(request, apr_id):
    apr = get_object_or_404(APR, id=apr_id)

    # Fetch related objects
    school_years = APRSchoolYear.objects.filter(apr=apr)
    action_plan_directives = ActionPlanDirective.objects.filter(apr=apr)
    priority_directives = PriorityDirective.objects.filter(apr=apr)
    directives = Directive.objects.filter(apr=apr)
    recommendations = Recommendation.objects.filter(apr=apr)
    action_plans = ActionPlan.objects.filter(apr=apr)

    # Fetch all progress and group dynamically
    all_progress = Progress.objects.filter(
        school_year__in=school_years
    ).select_related('priority_directive', 'directive', 'recommendation', 'action_plan', 'school_year'
                     ).prefetch_related('action_plan__actionplansteps_set')

    priority_directives_progress = group_progress_by_directive(
        all_progress.filter(priority_directive__in=priority_directives), 'priority_directive'
    )
    directives_progress = group_progress_by_directive(
        all_progress.filter(directive__in=directives), 'directive'
    )
    recommendations_progress = group_progress_by_directive(
        all_progress.filter(recommendation__in=recommendations), 'recommendation'
    )
    action_plans_progress = group_progress_by_directive(
        all_progress.filter(action_plan__in=action_plans), 'action_plan', include_steps=True
    )
    progress_statuses = ProgressStatus.objects.all()

    context = {
        'apr': apr,
        'school_years': school_years,
        'action_plan_directives': action_plan_directives,
        'priority_directives_progress': priority_directives_progress,
        'directives_progress': directives_progress,
        'recommendations_progress': recommendations_progress,
        'action_plans_progress': action_plans_progress,
        'progress_statuses': progress_statuses,
    }

    return render(request, 'apr/apr_progress_report.html', context)


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

@csrf_exempt  # This is optional if you're using the CSRF token properly
def update_progress_status(request):
    if request.method == 'POST':
        # Parse the data sent from the AJAX request
        data = json.loads(request.body)
        directive_id = data.get('directive_id')
        progress_status_value = data.get('progress_status')
        model_type = data.get('model_type')

        model_map = {
            'Directive': Directive,
            'Priority Directive': PriorityDirective,
            'Recommendation': Recommendation,
            'Action Plan': ActionPlan
        }

        model = model_map.get(model_type)
        if model is None:
            return JsonResponse({'success': False, 'error': 'Invalid model type'}, status=400)
        try:
            directive = model.objects.get(id=directive_id)
        except model.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Model not found'}, status=400)

        if directive:
            # Get the ProgressStatus instance corresponding to the status value
            try:
                progress_status = ProgressStatus.objects.get(status=progress_status_value)
            except ProgressStatus.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid progress status'})

            # Update the progress status
            directive.progress_status = progress_status
            directive.save()

            return JsonResponse({'success': True})

        # If the directive was not found, respond with an error
        return JsonResponse({'success': False, 'error': 'Directive not found'}, status=400)

    # If it's not a POST request, return a bad request response
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_actionplandirective_completed_date(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            directive_id = data.get('id')
            completed_date = data.get('completed_date')

            directive = ActionPlanDirective.objects.get(id=directive_id)
            directive.completed_date = datetime.strptime(completed_date, '%Y-%m-%d').date()
            directive.save()

            return JsonResponse({'message': 'Completed date updated successfully!'}, status=200)
        except ActionPlanDirective.DoesNotExist:
            return JsonResponse({'error': 'Directive not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)