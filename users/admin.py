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

#class SchoolAddressInLine(admin.StackedInline):
#    model = Address
#    can_delete = True
#    extra = 0
#    exclude = ['teacher']

class AccreditationInfoInline(admin.StackedInline):
    model = OtherAgencyAccreditationInfo
    extra = 0  # Number of extra forms to display


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ['country']

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    inlines = [AccreditationInfoInline]
    list_display = ('name', 'abbreviation', 'grade_levels', 'get_school_types','current_school_year','initial_accreditation_date','worthy_student_report_needed')
    list_editable = ('current_school_year','initial_accreditation_date', 'worthy_student_report_needed')

    # This enables the little "+" button to add Address directly
    autocomplete_fields = ['street_address', 'postal_address']

    def get_school_types(self, obj):
        return ", ".join([school_type.name for school_type in obj.school_type.all()])

    get_school_types.short_description = 'School Types'

@admin.register(SchoolTypeChoice)
class SchoolTypeChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    list_editable = ('code', 'name')
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




# Inline for UserProfile
class UserProfileInline(admin.StackedInline):  # You can also use TabularInline for a table-like layout
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"

# Custom UserProfile school filter
class SchoolFilter(admin.SimpleListFilter):
    title = 'School'  # Title of the filter in the admin
    parameter_name = 'school'  # URL query parameter

    def lookups(self, request, model_admin):
        # Return the available school choices for filtering
        schools = School.objects.all()
        return [(school.id, school.name) for school in schools]

    def queryset(self, request, queryset):
        # Filter queryset based on the selected school
        if self.value():
            return queryset.filter(profile__school_id=self.value())
        return queryset

# Custom UserAdmin
class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]  # Add the UserProfile inline
    list_display = ('username', 'School', 'id', 'group', 'is_active', "last_login", 'email')  # Add custom fields
    list_editable = ('is_active',)  # Allow toggling 'is_active' directly in the list view
    ordering = ('-is_active', 'last_login', 'username',)  # Custom ordering
    list_filter = (SchoolFilter, 'groups', 'is_active')  # Add custom filter for 'school'

    # Custom method to display the user's school
    def School(self, obj):
        # Check if the user has a profile and if the profile has a school
        if hasattr(obj, 'profile') and obj.profile and obj.profile.school:
            return obj.profile.school.name
        return "No School"
    School.short_description = "School"  # Set a custom column header

    # Custom method to display the user's groups
    def group(self, obj):
        return ", ".join(group.name for group in obj.groups.all())
    group.short_description = "Groups"  # Set a custom column header

# Unregister the default User admin and register the customized one
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

#TODO this only shows active user teachers, not teachers from the past
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



