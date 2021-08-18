from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


# Register your models here.
@admin.register(Country)
class Country(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    list_editable = ('code', 'region')

class AddressInLine(admin.StackedInline):
    model = Address
    can_delete = True
    extra = 0

@admin.register(School)
class School(admin.ModelAdmin):
    inlines = [AddressInLine,]
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


class ApplicationInLine(admin.StackedInline):
    model = Application
    can_delete = True
    extra=0

class CollegeAttendedInLine(admin.StackedInline):
    model = CollegeAttended
    can_delete = True
    extra=0

class SchoolOfEmploymentInLine(admin.StackedInline):
    model = SchoolOfEmployment
    can_delete = True
    extra=0

@admin.register(Teacher)
class Teacher(admin.ModelAdmin):
    inlines = [AddressInLine, ApplicationInLine,CollegeAttendedInLine, SchoolOfEmploymentInLine]



