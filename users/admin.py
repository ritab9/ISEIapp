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
    list_display = ('name', 'abbreviation',)
    list_editable = ('abbreviation',)



#class TeacherInline(admin.StackedInline):
#    model = Teacher
#    can_delete = True

class UserAdmin(AuthUserAdmin):
    #inlines = [TeacherInline, AddressInLine]
    list_display = ('username', 'School', 'id','group', 'is_active')
    list_editable = ('is_active',)

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
    inlines = [TeacherAddressInLine, CollegeAttendedInLine, SchoolOfEmploymentInLine]
    list_display = ('name', 'school', 'active')
    list_editable = ('school', 'active')
    list_display_links = ('name',)


