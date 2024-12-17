#services/admin
from django.contrib import admin
from .models import *


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_filter = ['type', ]

class TestMaterialTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'update')  # Display these fields
    list_editable = ('price',)  # Make these fields editable

admin.site.register(TestMaterialType, TestMaterialTypeAdmin)


class ReusableTestBookletOrderedInline(admin.TabularInline):
    model = ReusableTestBookletOrdered
    extra = 1  # How many rows to show


class AnswerSheetOrderedInline(admin.TabularInline):
    model = AnswerSheetOrdered
    extra = 1


class DirectionBookletOrderedInline(admin.TabularInline):
    model = DirectionBookletOrdered
    extra = 1


class TestOrderAdmin(admin.ModelAdmin):
    inlines = [
        ReusableTestBookletOrderedInline,
        AnswerSheetOrderedInline,
        DirectionBookletOrderedInline,
    ]


admin.site.register(TestOrder, TestOrderAdmin)
