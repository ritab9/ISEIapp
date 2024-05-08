from django.contrib import admin
from .models import *


class ReportDueDateInline(admin.TabularInline):
    model = ReportDueDate
    extra = 1  # Number of extra empty rows to display

class ReportAdmin(admin.ModelAdmin):
    inlines = [ReportDueDateInline]

class ReportDueDateAdmin(admin.ModelAdmin):
    list_display = ['region','report', 'due_date','opening_report']
    list_display_links = ['report']
    list_filter = ['region']
    list_editable = ['due_date', 'opening_report']

admin.site.register(Report, ReportAdmin)
admin.site.register(ReportDueDate, ReportDueDateAdmin)

@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ['report','school_year', 'school']
# customize the AnnualReport admin section here


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name','annual_report']
    list_filter = ['annual_report']
