from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


# Register your models here.
@admin.register(Country)
class Country(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    list_editable = ('code', 'region')

class SchoolAddressInLine(admin.StackedInline):
    model = Address
    can_delete = True
    extra = 0
    exclude = ['teacher']

@admin.register(School)
class School(admin.ModelAdmin):
    inlines = [SchoolAddressInLine,]
    list_display = ('id', 'name', 'abbreviation', 'foundation')
    list_editable = ('abbreviation', 'foundation')



#class TeacherInline(admin.StackedInline):
#    model = Teacher
#    can_delete = True

class UserAdmin(AuthUserAdmin):
    #inlines = [TeacherInline, AddressInLine]
    list_display = ('username', 'School', 'id','group', 'is_active', "last_login", 'email')
    list_editable = ('is_active',)
    ordering = ('-is_active','last_login','username',)

    #def Name(self,obj):
    #    return obj.teacher

    def School(self, obj):
        return obj.teacher.school

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



