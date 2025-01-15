from django.contrib import admin
from .models import *

class FinancialTwoYearDataKeyAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'order_number')
    list_editable = ('name', 'order_number')  # Make both fields editable directly in the list view
    search_fields = ('name',)

class FinancialAdditionalDataKeyAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'order_number')
    list_editable = ('name', 'order_number')  # Make both fields editable directly in the list view
    search_fields = ('name',)

# Inline for TeamMember
class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1  # Number of empty forms displayed by default


# Inline for CoordinatingTeam
class CoordinatingTeamInline(admin.TabularInline):
    model = CoordinatingTeam
    extra = 1  # Number of empty forms displayed by default

# Admin for CoordinatingTeam with filter by SelfStudy
class CoordinatingTeamAdmin(admin.ModelAdmin):
    list_display = ('coordinating_team', 'selfstudy')
    list_filter = ('selfstudy',)  # Filter by SelfStudy
    inlines = [TeamMemberInline]

# Inline for SchoolProfile
class SchoolProfileInline(admin.TabularInline):
    model = SchoolProfile
    extra = 1  # Number of empty forms displayed by default

# Admin for SelfStudy with inlines for CoordinatingTeam and SchoolProfile
class SelfStudyAdmin(admin.ModelAdmin):
    list_display = ('accreditation', 'last_updated', 'submission_date')
    list_filter = ('accreditation', 'last_updated')  # Add filters
    search_fields = ('accreditation__school__name',)  # Enable searching by school name (assuming you have this field)
    inlines = [CoordinatingTeamInline, SchoolProfileInline]
    ordering = ('-last_updated',)  # Order by last_updated descending by default


# Register your models with the admin site
admin.site.register(FinancialTwoYearDataKey, FinancialTwoYearDataKeyAdmin)
admin.site.register(FinancialAdditionalDataKey, FinancialAdditionalDataKeyAdmin)
admin.site.register(CoordinatingTeam, CoordinatingTeamAdmin)
admin.site.register(SelfStudy, SelfStudyAdmin)


class IndicatorEvaluationAdmin(admin.ModelAdmin):
    list_display = ('selfstudy', 'standard', 'indicator', 'score', 'reference_documents', 'explanation')
    list_filter = ('selfstudy', 'standard',)  # You can filter by these fields
    search_fields = ('selfstudy__accreditation__school__name', 'standard')  # Search by school name or indicator name

    def get_score_display(self, obj):
        return obj.get_score_display() or 'Not Scored'
    get_score_display.short_description = 'Score'  # Change column name to 'Score'

admin.site.register(IndicatorEvaluation, IndicatorEvaluationAdmin)
