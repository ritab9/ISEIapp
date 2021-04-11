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
    list_display = ('id','username', 'first_name', 'last_name')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
