from django.contrib import admin
from teachercert.models import *

# Register your models here.

@admin.register(SchoolYear)
class SchoolYear(admin.ModelAdmin):
    list_display = ('name','active_year')
    list_editable = ('active_year',)
    list_display_links = ('name',)

@admin.register(PDAType)
class PDAType(admin.ModelAdmin):
    list_display = ('category', 'description', 'ceu_value')
    fields = ['category', 'description','evidence', 'ceu_value']


class PDAInstanceInline(admin.StackedInline):
    model = PDAInstance
    can_delete = False
    extra = 1


@admin.register(PDARecord)
class PDARecord(admin.ModelAdmin):
    inlines = [PDAInstanceInline]
    list_display = ('teacher', 'school_year', 'date_submitted','principal_signed')
    list_editable = ('date_submitted', 'principal_signed')
    list_display_links = ('teacher',)
