from django.contrib import admin
from teachercert.models import *
from django.utils.html import format_html
from teachercert.forms import RenewalForm
from django import forms
from users.models import *
# Register your models here.

@admin.register(SchoolYear)
class SchoolYear(admin.ModelAdmin):
    list_display = ('name','active_year', 'start_date', 'end_date',)
    list_editable = ('active_year','start_date', 'end_date', )
    list_display_links = ('name',)

#PDA Report Model Registration
@admin.register(PDAType)
class PDAType(admin.ModelAdmin):
    list_display = ('category', 'description', 'ceu_value')
    fields = ['category', 'description','evidence', 'ceu_value']

@admin.register(AcademicClass)
class AcademicClass(admin.ModelAdmin):
    model = AcademicClass
    list_display = ('teacher','name', 'university', 'date_completed', 'transcript_requested', 'transcript_received')
    list_display_links = ('name',)
    list_editable = ('university', 'date_completed', 'transcript_requested', 'transcript_received')

class PDAInstanceInline(admin.StackedInline):
    model = PDAInstance
    can_delete = False
    extra = 0
    readonly_fields = ['created_at', 'updated_at', ]

@admin.register(PDAReport)
class PDAReport(admin.ModelAdmin):
    inlines = [PDAInstanceInline,]
    list_display = ('teacher', 'school_year', 'date_submitted','principal_reviewed', 'isei_reviewed', 'updated_at')
    list_editable = ('date_submitted', 'principal_reviewed', 'isei_reviewed', 'school_year')
    list_display_links = ('teacher',)
    readonly_fields = ['created_at', 'updated_at', ]

@admin.register(EmailMessage)
class EmailMessage(admin.ModelAdmin):
    list_display = ('name', 'message')
    list_editable = ('message',)
    list_display_links = ('name', )


#teacher Certification Model Registration
@admin.register(Requirement)
class Requirement(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(Renewal)
class Renewal(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(CertificationType)
class CertificationType(admin.ModelAdmin):
    list_display = ('name', 'years_valid', 'renewal_conditions' )

    #not currently added to the list
    def requirements(self, obj):
        requirements = []
        for r in obj.requirements_set.all():
            requirements.append(r.name)
            requirements.append('<br>')
        return format_html(''.join(requirements))

    def renewal_conditions(self, obj):
        renew = []
        for r in obj.renewal_set.all():
            renew.append(r.name)
            renew.append('<br>')
        return format_html(''.join(renew))

@admin.register(ElementaryMethod)
class ElementaryMethod(admin.ModelAdmin):
    list_display = ('name', 'required')
    list_editable = ('required',)

@admin.register(Endorsement)
class Endorsement(admin.ModelAdmin):
    list_display = ('name',)


class TEndorsementInLine(admin.StackedInline):
    model = TEndorsement
    extra = 0

@admin.register(TCertificate)
class TCertificate(admin.ModelAdmin):
    inlines = [TEndorsementInLine]
    list_display = ('teacher', 'certification_type', 'issue_date','renewal_date', 'archived','renewal_requirements')
    list_editable = ('certification_type','archived', 'issue_date','renewal_date', 'renewal_requirements')
    list_display_links = ('teacher',)

@admin.register(TeacherCertificationApplication)
class TeacherCertificationApplication(admin.ModelAdmin):
    model = TeacherCertificationApplication
    list_display = ('id','teacher', 'initial', 'date', 'billed', 'closed')
    list_editable = ('initial', 'date', 'billed', 'closed')
    list_display_links = ('teacher',)