from django.contrib import admin
from .models import *

@admin.register(AnnualVisit)
class AnnualVisitAdmin(admin.ModelAdmin):
    list_display = ("school", "school_year", "visit_date", "representative", "created_at")
    list_editable = ("visit_date", "representative")
    list_filter = ("school_year", "school", 'representative')
    search_fields = ("school__name", "representative")


@admin.register(SchoolDocument)
class SchoolDocumentAdmin(admin.ModelAdmin):
    list_display = ("school", "link")
    search_fields = ("school__name",)
    list_editable = ("link",)  # Makes the link field editable directly in the list


