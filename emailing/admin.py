from django.contrib import admin
from .models import MessageTemplate

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject")
    search_fields = ("name", "subject")
