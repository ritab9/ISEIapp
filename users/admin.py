from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


# Register your models here.
class CountryInline(admin.TabularInline):
    model = Country

@admin.register(Region)
class Region(admin.ModelAdmin):
    inlines = [CountryInline]
    list_display = ('name',)

@admin.register(Country)
class Country(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'student_occurrence', 'student_occurrence_log')
    list_editable = ('code', 'region')
    search_fields = ('name',)
    list_filter = ('region',)


admin.site.register(TNCounty)

class SchoolAddressInLine(admin.StackedInline):
    model = Address
    can_delete = True
    extra = 0
    exclude = ['teacher']

class AccreditationInfoInline(admin.StackedInline):
    model = OtherAgencyAccreditationInfo
    extra = 0  # Number of extra forms to display

@admin.register(School)
class School(admin.ModelAdmin):
    inlines = [AccreditationInfoInline, SchoolAddressInLine,]
    list_display = ('name', 'abbreviation', 'type', 'current_school_year','initial_accreditation_date','worthy_student_report_needed')
    list_editable = ('current_school_year','initial_accreditation_date', 'worthy_student_report_needed')

@admin.register(AccreditationAgency)
class AccreditationAgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']

@admin.register(OtherAgencyAccreditationInfo)
class OtherAgencyAccreditationInfoAdmin(admin.ModelAdmin):
    list_display = ('school', 'agency', 'start_date', 'end_date', 'current_accreditation')
    list_filter = ('agency', 'current_accreditation', 'start_date', 'end_date')
    list_editable= ('current_accreditation', 'start_date', 'end_date')
    search_fields = ('school__name', 'agency__name', 'agency__abbreviation')
    ordering = ('school', 'agency', 'start_date')





class UserProfileInline(admin.StackedInline):  # Or use TabularInline
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"

class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'School', 'School2', 'id','group', 'is_active', "last_login", 'email')
    list_editable = ('is_active',)
    ordering = ('-is_active','last_login','username',)

    def School(self, obj):
        return obj.profile.school

    def School2(self, obj):
        if obj.teacher:
            return obj.teacher.school

    #    selfstudy_teammember = obj.selfstudy_teammember_set.last()
    #    if selfstudy_teammember:
    #        return selfstudy_teammember.team.selfstudy.accreditation.school

    def group(self,obj):
        groups = []
        for group in obj.groups.all():
            groups.append(group.name)
            groups.append(" ")
        return ''.join(groups)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


#class TeacherCertificationApplicationInLine(admin.StackedInline):
#    model = TeacherCertificationApplication
#    can_delete = True
#    extra=0

class CollegeAttendedInLine(admin.StackedInline):
    model = CollegeAttended
    can_delete = True
    extra=0

class SchoolOfEmploymentInLine(admin.StackedInline):
    model = SchoolOfEmployment
    can_delete = True
    extra=0

class TeacherAddressInLine(admin.StackedInline):
    model = Address
    can_delete = True
    extra = 0
    exclude = ['school']


@admin.register(Teacher)
class Teacher(admin.ModelAdmin):
    inlines = [TeacherAddressInLine, CollegeAttendedInLine, SchoolOfEmploymentInLine,]
    list_display = ('name', 'school','joined_at')
    list_editable = ('school',)
    list_display_links = ('name',)
    list_filter =('school',)
    ordering = ('last_name','joined_at',)
    search_fields = ['first_name','last_name' ]  # Added this line

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_active = True)

@admin.register(CollegeAttended)
class CollegeAttended(admin.ModelAdmin):
    model = CollegeAttended
    can_delete=True
    list_display = ('teacher','name', 'level','degree', 'transcript_requested', 'transcript_received', 'transcript_processed', 'start_date', 'end_date')
    list_editable = ('transcript_requested', 'transcript_received', 'transcript_processed')
    list_display_links = ('name', 'teacher')
    list_filter = ( 'transcript_requested', 'transcript_received', 'transcript_processed', 'name',)
    search_fields = ['name']


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(teacher__user__is_active = True)

@admin.register(SchoolOfEmployment)
class SchoolOfEmployment(admin.ModelAdmin):
    model = SchoolOfEmployment
    can_delete = True
    list_display =('teacher', 'name','start_date', 'end_date', 'courses')
    list_editable =('start_date', 'end_date',)
    search_fields = ['name']



