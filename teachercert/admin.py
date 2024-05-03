from django.contrib import admin
from teachercert.models import *
from django.utils.html import format_html
from teachercert.forms import RenewalForm
from django import forms
from users.models import *
# Register your models here.

@admin.register(SchoolYear)
class SchoolYear(admin.ModelAdmin):
    list_display = ('name','current_school_year','active_year', 'start_date', 'end_date',)
    list_editable = ('current_school_year','active_year','start_date', 'end_date', )
    list_display_links = ('name',)

@admin.register(CEUCategory)
class CEUCategory(admin.ModelAdmin):
    list_display = ('id','name',)
    #list_editable = ('name',)
    list_display_links = ('id',)


@admin.register(CEUType)
class CEUType(admin.ModelAdmin):
    list_display = ('ceu_category', 'description', 'ceu_value','evidence')
    #list_editable = ('ceu_value', 'evidence')
    list_display_links =('description',)


@admin.register(AcademicClass)
class AcademicClass(admin.ModelAdmin):
    model = AcademicClass
    list_display = ('teacher','name', 'university', 'date_completed', 'transcript_requested', 'transcript_received')
    list_display_links = ('name',)
    list_editable = ('transcript_requested', 'transcript_received')
    list_filter = ('transcript_requested', 'transcript_received', 'university')
    search_fields = ['name', 'university']
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)


class CEUInstanceInline(admin.StackedInline):
    model = CEUInstance
    can_delete = True
    extra = 0
    readonly_fields = ['created_at', 'updated_at', ]

@admin.register(CEUReport)
class CEUReport(admin.ModelAdmin):
    inlines = [CEUInstanceInline,]
    list_display = ('teacher', 'school_year', 'date_submitted','principal_reviewed', 'isei_reviewed', 'updated_at')
    list_editable = ('date_submitted', 'principal_reviewed', 'isei_reviewed',)
    list_display_links = ('teacher',)
    readonly_fields = ['created_at', 'updated_at', ]
    list_filter = ('school_year', 'principal_reviewed', 'isei_reviewed')
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name' ]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)

@admin.register(EmailMessageTemplate)
class EmailMessageTemplate(admin.ModelAdmin):
    list_display = ( 'sender', 'receiver', 'name', 'message',)
    list_editable = ('sender', 'receiver', 'name' )
    list_display_links = ('message', )


#teacher Certification Model Registration
@admin.register(Requirement)
class Requirement(admin.ModelAdmin):
    list_display = ('name', 'category', )
    ordering = ('category',)
    #def certification_types(self, obj):
    #    certification_types =[]
    #    for c in obj.certification_type_set.all():
    #        certification_types.append(c.name)
    #        certification_types.append('<br>')
    #    return format_html("".join(certification_types))


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


@admin.register(TEndorsement)
class TEndorsement(admin.ModelAdmin):
    list_display = ('certificate','endorsement','range')
    list_editable = ('endorsement','range')
    #def teacher(self, obj):
    #    return self.certificate.teacher
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(certificate__teacher__user__is_active = True)


@admin.register(TCertificate)
class TCertificate(admin.ModelAdmin):
    inlines = [TEndorsementInLine]
    list_display = ('teacher', 'certification_type', 'issue_date','renewal_date', 'archived',)
    list_editable = ('archived', )
    list_display_links = ('teacher',)
    list_filter = ('certification_type','archived')
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name' ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)

@admin.register(TeacherCertificationApplication)
class TeacherCertificationApplication(admin.ModelAdmin):
    model = TeacherCertificationApplication
    list_display = ('School', 'teacher',  'billed', 'date', 'endors_level','isei_revision_date', 'closed')
    list_editable = ('date', 'billed', 'closed', 'endors_level')
    list_display_links = ('teacher',)
    ordering = ('billed','closed', 'teacher__school')
    list_filter = ('billed', 'closed', 'teacher__school')
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name' ]


    def School(self, obj):
        return obj.teacher.school

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)



@admin.register(TeacherBasicRequirement)
class TeacherBasicRequirement(admin.ModelAdmin):
    list_display = ('teacher', 'basic_requirement', 'met')
    list_editable = ('met',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)

@admin.register(StandardChecklist)
class StandardCheckList(admin.ModelAdmin):
    list_display = ("teacher","sda", 'ba_degree', 'no_Ds', 'experience',
                    'religion_and_health', 'education_credits',
                    'credits18', "credits12", 'elementary_methods', 'sec_methods'
                    )

