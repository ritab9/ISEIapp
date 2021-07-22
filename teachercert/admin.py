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
    extra = 0
    readonly_fields = ['created_at', 'updated_at', ]

class AcademicClassInLine(admin.StackedInline):
    model = AcademicClass
    extra = 0


@admin.register(PDAReport)
class PDAReport(admin.ModelAdmin):
    inlines = [PDAInstanceInline, AcademicClassInLine]
    list_display = ('teacher', 'school_year', 'date_submitted','principal_reviewed', 'isei_reviewed', 'updated_at')
    list_editable = ('date_submitted', 'principal_reviewed', 'isei_reviewed')
    list_display_links = ('teacher','school_year')
    readonly_fields = ['created_at', 'updated_at', ]

@admin.register(EmailMessages)
class EmailMessages(admin.ModelAdmin):
    list_display = ('name', 'message')
    list_editable = ('message',)
    list_display_links = ('name', )
