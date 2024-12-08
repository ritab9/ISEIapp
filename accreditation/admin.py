from django.contrib import admin
from .models import Accreditation, AccreditationTerm


class AccreditationAdmin(admin.ModelAdmin):
    list_display = ['school', 'term', 'term_start_date', 'term_end_date']
    list_filter = ['term_start_date', 'term_end_date']
    search_fields = ['school__name']

admin.site.register(Accreditation, AccreditationAdmin)

@admin.register(AccreditationTerm)
class AccreditationTermAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']
