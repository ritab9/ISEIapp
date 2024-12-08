
from django.contrib import admin
from .models import *


import nested_admin


class ProgressInline(nested_admin.NestedStackedInline):
    model = Progress
    extra = 1


class PriorityDirectiveInline(nested_admin.NestedStackedInline):
    model = PriorityDirective
    inlines = [ProgressInline]
    extra = 1


class DirectiveInline(nested_admin.NestedStackedInline):
    model = Directive
    inlines = [ProgressInline]
    extra = 1


class RecommendationInline(nested_admin.NestedStackedInline):
    model = Recommendation
    inlines = [ProgressInline]
    extra = 1


class ActionPlanInline(nested_admin.NestedStackedInline):
    model = ActionPlan
    inlines = [ProgressInline]
    extra = 1


class APRAdmin(nested_admin.NestedModelAdmin):
    inlines = [PriorityDirectiveInline, DirectiveInline, RecommendationInline, ActionPlanInline]

admin.site.register(APR, APRAdmin)


class ProgressStatusAdmin(admin.ModelAdmin):
    list_display = ['id','status']
    list_editable = ['status']

admin.site.register(ProgressStatus, ProgressStatusAdmin)

class APRSchoolYearAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    list_editable = ['name']



# Inline for Action Plan Steps
class ActionPlanStepsInline(admin.TabularInline):
    model = ActionPlanSteps
    extra = 1  # Number of empty forms for adding steps
    fields = ['number', 'person_responsible', 'action_steps', 'timeline', 'resources']
    readonly_fields = ['number']  # If you want to make the step number read-only

# Admin for Action Plans
@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'apr', 'number', 'standard', 'objective']
    search_fields = ['apr__accreditation__name', 'standard', 'objective']
    inlines = [ActionPlanStepsInline]

# Admin for Action Plan Steps (standalone)
#@admin.register(ActionPlanSteps)
#class ActionPlanStepsAdmin(admin.ModelAdmin):
#    list_display = ['id', 'action_plan', 'number', 'person_responsible', 'action_steps']
#    search_fields = ['person_responsible', 'action_steps']
#    list_filter = ['action_plan']  # Add filter to easily view orphaned steps
#    actions = ['delete_orphaned_steps']
    # Custom admin action to delete steps without Action Plans
    #def delete_orphaned_steps(self, request, queryset):
    #    orphaned_steps = queryset.filter(action_plan__isnull=True)
    #    count = orphaned_steps.count()
    #    orphaned_steps.delete()
    #    self.message_user(request, f"{count} orphaned steps were deleted.")
    #delete_orphaned_steps.short_description = "Delete orphaned steps (no Action Plan)"


