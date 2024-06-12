from django.contrib import admin
from .models import *


class ReportDueDateInline(admin.TabularInline):
    model = ReportDueDate
    extra = 1  # Number of extra empty rows to display

class ReportAdmin(admin.ModelAdmin):
    inlines = [ReportDueDateInline]

class ReportDueDateAdmin(admin.ModelAdmin):
    list_display = ['region','report_type', 'due_date','opening_report']
    list_display_links = ['report_type']
    list_filter = ['region']
    list_editable = ['due_date', 'opening_report']

admin.site.register(ReportDueDate, ReportDueDateAdmin)

class ReportTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'order_number','for_all_schools', 'isei_created', 'view_name']
    list_editable = ['order_number', 'for_all_schools', 'isei_created', 'view_name', 'code']
admin.site.register(ReportType, ReportTypeAdmin)

@admin.register(AnnualReport)
class AnnualReportAdmin(admin.ModelAdmin):
    list_display = ['report_type','school_year', 'school', 'submit_date']
    list_editable = ['submit_date']
    list_filter = ('school_year', 'report_type', 'school',)
# customize the AnnualReport admin section here


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name','annual_report']
    list_filter = ['annual_report']



class VacationsInline(admin.StackedInline):
    model = Vacations


class InserviceDiscretionaryDaysInline(admin.StackedInline):
    model = InserviceDiscretionaryDays


class AbbreviatedDaysInline(admin.StackedInline):
    model = AbbreviatedDays


class SundaySchoolDaysInline(admin.StackedInline):
    model = SundaySchoolDays


class EducationalEnrichmentActivityInline(admin.StackedInline):
    model = EducationalEnrichmentActivity


@admin.register(Day190)
class Day190Admin(admin.ModelAdmin):

    inlines = [VacationsInline, InserviceDiscretionaryDaysInline, SundaySchoolDaysInline, AbbreviatedDaysInline,
               EducationalEnrichmentActivityInline]