from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


# Register your models here.
@admin.register(School)
class School(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'address')
    list_editable = ('abbreviation', 'address')

class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = True

class UserAdmin(AuthUserAdmin):
    inlines = [TeacherInline]
    list_display = ('username', 'first_name', 'last_name',  'School', 'id','group', 'is_active')
    list_editable = ('is_active',)

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
