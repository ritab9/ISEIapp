from django.contrib import admin
from .models import SelfStudy, CoordinatingTeam, TeamMember, SchoolProfile, FinancialTwoYearDataKey, FinancialAdditionalDataKey

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

# Inline for FinancialInformationEntries
#class FinancialInformationEntriesInline(admin.TabularInline):
#    model = FinancialInformationEntries
#    extra = 1  # Number of empty forms displayed by default

# Inline for FinancialDataEntries
#class FinancialDataEntriesInline(admin.TabularInline):
#    model = FinancialDataEntries
#    extra = 1  # Number of empty forms displayed by default

# Inline for CoordinatingTeam
class CoordinatingTeamInline(admin.TabularInline):
    model = CoordinatingTeam
    extra = 1  # Number of empty forms displayed by default

# Admin for CoordinatingTeam with filter by SelfStudy
class CoordinatingTeamAdmin(admin.ModelAdmin):
    list_display = ('coordinating_team', 'self_study')
    list_filter = ('self_study',)  # Filter by SelfStudy
    inlines = [TeamMemberInline]

# Inline for SchoolProfile
class SchoolProfileInline(admin.TabularInline):
    model = SchoolProfile
    extra = 1  # Number of empty forms displayed by default

# Admin for SelfStudy with inlines for CoordinatingTeam and SchoolProfile
class SelfStudyAdmin(admin.ModelAdmin):
    list_display = ('accreditation', 'last_updated', 'submission_date')
    inlines = [CoordinatingTeamInline, SchoolProfileInline]


# Register your models with the admin site
admin.site.register(FinancialTwoYearDataKey, FinancialTwoYearDataKeyAdmin)
admin.site.register(FinancialAdditionalDataKey, FinancialAdditionalDataKeyAdmin)
admin.site.register(CoordinatingTeam, CoordinatingTeamAdmin)
admin.site.register(SelfStudy, SelfStudyAdmin)
