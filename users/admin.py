from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(School)
class School(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'address')
    list_editable = ('abbreviation', 'address')