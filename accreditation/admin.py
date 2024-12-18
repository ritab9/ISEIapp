from django.contrib import admin
from .models import *


class AccreditationAdmin(admin.ModelAdmin):
    list_display = ['school', 'term', 'term_start_date', 'term_end_date']
    list_filter = ['term_start_date', 'term_end_date']
    search_fields = ['school__name']

admin.site.register(Accreditation, AccreditationAdmin)

@admin.register(AccreditationTerm)
class AccreditationTermAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']


#Self Study models

class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_editable = ('name',)
    #list_display_links = ('id',)


class LevelInline(admin.TabularInline):
    model = Level
    extra = 4

class IndicatorAdmin(admin.ModelAdmin):
    inlines = [LevelInline]
    list_display = ('code', 'key_word')
    list_editable = ('key_word',)
    list_filter = ('standard', 'school_type',)

class IndicatorInline(admin.StackedInline):
    model = Indicator
    extra = 1


class StandardAdmin(admin.ModelAdmin):
    inlines = [IndicatorInline]

admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Standard, StandardAdmin)
admin.site.register(SchoolType, SchoolTypeAdmin)
