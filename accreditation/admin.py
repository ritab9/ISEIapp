from django.contrib import admin
from .models import *

class AccreditationVisitingTeamInline(admin.TabularInline):
    model = AccreditationVisitingTeam
    extra = 1  # how many empty rows to show
    autocomplete_fields = ["user"]

class AccreditationAdmin(admin.ModelAdmin):
    list_display = ['school', 'status', 'term', 'term_start_date', 'term_end_date', 'evidence_documents_link']
    list_filter = ['term_start_date', 'term_end_date', 'status']
    list_editable = ['status', 'evidence_documents_link']
    search_fields = ['school__name', ]
    inlines = [AccreditationVisitingTeamInline]

admin.site.register(Accreditation, AccreditationAdmin)

@admin.register(AccreditationTerm)
class AccreditationTermAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']

#Self Study models

class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    list_editable = ('name', 'code')
    #list_display_links = ('id',)

@admin.register(IndicatorScore)
class IndicatorScoreAdmin(admin.ModelAdmin):
    list_display = ('score', 'get_score_display', 'comment')
    list_filter = ('score',)
    ordering = ('-score',)

#class LevelInline(admin.TabularInline):
#    model = Level
#    extra = 4

class IndicatorAdmin(admin.ModelAdmin):
    #inlines = [LevelInline]
    list_display = ( 'key_word','code', 'school_type', 'version', 'active')
    list_editable = ('code','version', 'active', 'school_type')
    list_filter = ('standard', 'school_type',)

class IndicatorInline(admin.StackedInline):
    model = Indicator
    extra = 1

class StandardAdmin(admin.ModelAdmin):
    inlines = [IndicatorInline]

admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Standard, StandardAdmin)
admin.site.register(SchoolType, SchoolTypeAdmin)

@admin.register(InfoPage)
class InfoPageAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AccreditationApplication)
class AccreditationApplicationAdmin(admin.ModelAdmin):
    list_display = ('school', 'school_year', 'date', 'accreditation' )
    list_filter = ('school_year', 'date')
    search_fields = ('school__name',)


class RequiredEvidenceInLine(admin.StackedInline):
    model = RequiredEvidence
    extra = 1

class RequiredEvidenceCategoryAdmin(admin.ModelAdmin):
    inlines = [RequiredEvidenceInLine]

admin.site.register(RequiredEvidenceCategory, RequiredEvidenceCategoryAdmin)