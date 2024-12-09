#admin.py


from django.contrib import admin
from .models import *

# 1. Register ProgressStatus on its own
@admin.register(ProgressStatus)
class ProgressStatusAdmin(admin.ModelAdmin):
    list_display = ['status']
    search_fields = ['status']

# 2. Register APR with inlines for PriorityDirective, Directive, Recommendation, ActionPlan
class ProgressInline(admin.StackedInline):
    model = Progress
    extra = 1

class PriorityDirectiveInline(admin.StackedInline):
    model = PriorityDirective
    extra = 1
    inlines = [ProgressInline]

class DirectiveInline(admin.StackedInline):
    model = Directive
    extra = 1
    inlines = [ProgressInline]

class RecommendationInline(admin.StackedInline):
    model = Recommendation
    extra = 1
    inlines = [ProgressInline]

class ActionPlanInline(admin.StackedInline):
    model = ActionPlan
    extra = 1
    inlines = [ProgressInline]

@admin.register(APR)
class APRAdmin(admin.ModelAdmin):
    list_display = ['accreditation', 'accreditation_school']
    search_fields = ['accreditation__school']  # Filtering by accreditation school
    inlines = [PriorityDirectiveInline, DirectiveInline, RecommendationInline, ActionPlanInline]

    def accreditation_school(self, obj):
        return obj.accreditation.school
    accreditation_school.admin_order_field = 'accreditation__school'  # Allow sorting by school

# 3. Register Directive, PriorityDirective, Recommendation on their own with Progress as inline
@admin.register(PriorityDirective)
class PriorityDirectiveAdmin(admin.ModelAdmin):
    list_display = ['number', 'apr', 'progress_status', 'description']
    list_filter = ['apr']
    inlines = [ProgressInline]

@admin.register(Directive)
class DirectiveAdmin(admin.ModelAdmin):
    list_display = ['number', 'apr', 'progress_status', 'description']
    list_filter = ['apr']
    inlines = [ProgressInline]

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['number', 'apr', 'progress_status', 'description']
    list_filter = ['apr']
    inlines = [ProgressInline]

# 4. Register ActionPlan with ActionPlanSteps and Progress as Inlines
class ActionPlanStepsInline(admin.StackedInline):
    model = ActionPlanSteps
    extra = 1

@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ['number', 'apr', 'standard', 'objective', 'progress_status']
    list_filter = ['apr']
    inlines = [ActionPlanStepsInline, ProgressInline]

# 5. Register ActionPlanSteps and Progress separately if needed
@admin.register(ActionPlanSteps)
class ActionPlanStepsAdmin(admin.ModelAdmin):
    list_display = ['action_plan', 'number', 'person_responsible']
    search_fields = ['action_plan__number', 'person_responsible']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['school_year', 'description', 'priority_directive', 'directive', 'recommendation', 'action_plan']
    list_filter = ['school_year', 'priority_directive', 'directive', 'recommendation', 'action_plan']
    search_fields = ['description']

