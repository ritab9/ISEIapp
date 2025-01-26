from django.contrib import admin
from .models import *

class FinancialTwoYearDataKeyAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'order_number', 'active')
    list_editable = ('name', 'order_number', 'active')  # Make both fields editable directly in the list view
    search_fields = ('name',)

class FinancialAdditionalDataKeyAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'order_number', 'active')
    list_editable = ('name', 'order_number', 'active')  # Make both fields editable directly in the list view
    search_fields = ('name',)

admin.site.register(FinancialTwoYearDataKey, FinancialTwoYearDataKeyAdmin)
admin.site.register(FinancialAdditionalDataKey, FinancialAdditionalDataKeyAdmin)

admin.site.register(StandardNarrative)


# Inline for SchoolProfile
class SchoolProfileInline(admin.TabularInline):
    model = SchoolProfile
    extra = 1  # Number of empty forms displayed by default

# Admin for SelfStudy with inlines for CoordinatingTeam and SchoolProfile
class SelfStudyAdmin(admin.ModelAdmin):
    list_display = ('accreditation', 'last_updated', 'submission_date')
    list_filter = ('accreditation', 'last_updated')  # Add filters
    search_fields = ('accreditation__school__name',)  # Enable searching by school name (assuming you have this field)
    inlines = [SchoolProfileInline]
    ordering = ('-last_updated',)  # Order by last_updated descending by default

# Register your models with the admin site

admin.site.register(SelfStudy, SelfStudyAdmin)


class IndicatorEvaluationAdmin(admin.ModelAdmin):
    list_display = ('selfstudy', 'standard', 'indicator', 'score', 'reference_documents', 'explanation')
    list_filter = ('selfstudy', 'standard',)  # You can filter by these fields
    search_fields = ('selfstudy__accreditation__school__name', 'standard')  # Search by school name or indicator name

    def get_score_display(self, obj):
        return obj.get_score_display() or 'Not Scored'
    get_score_display.short_description = 'Score'  # Change column name to 'Score'

admin.site.register(IndicatorEvaluation, IndicatorEvaluationAdmin)


class ActionPlanInstructionSectionAdmin(admin.ModelAdmin):
    list_display = ['number', 'content']  # Show order number and truncated content
    ordering = ['number']  # Order by the 'number' field
    search_fields = ['content']  # Allow search by content

class ActionPlanInstructionsAdmin(admin.ModelAdmin):
    list_display = ['link_text', 'procedure_title', 'procedure_title_1', 'procedure_title_2']
    filter_horizontal = ['paragraphs', 'procedure_group_1', 'procedure_group_2']  # Simplified selection of related sections

admin.site.register(ActionPlanInstructionSection, ActionPlanInstructionSectionAdmin)
admin.site.register(ActionPlanInstructions, ActionPlanInstructionsAdmin)


#Coordinating Team Models
class SelfStudy_TeamMemberInline(admin.TabularInline):
    model = SelfStudy_TeamMember
    extra = 1
    fields = ('user', 'active')

class SelfStudy_TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'selfstudy', 'list_team_members')  # Adding list of members
    inlines = [SelfStudy_TeamMemberInline]  # Include the inline form for team members
    list_filter = ('selfstudy', )  # Filter teams by selfstudy

    def list_team_members(self, obj):
        """Custom method to list all members of the team."""
        members = SelfStudy_TeamMember.objects.filter(team=obj)  # Get team members for the team
        return ", ".join(member.user.get_full_name() for member in members)

    list_team_members.short_description = "Team Members"  # Change column header to 'Team Members'


admin.site.register(SelfStudy_Team, SelfStudy_TeamAdmin)
admin.site.register(SelfStudy_TeamMember)
