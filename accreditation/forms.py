from django import forms
from django.forms import DateInput
from .models import Accreditation, AccreditationApplication
from users.models import School, Address


class AccreditationForm(forms.ModelForm):
    class Meta:
        model = Accreditation
        fields = ['school', 'visit_start_date', 'visit_end_date',
                  'term', 'term_start_date', 'term_end_date', 'term_comment',
                  'coa_approval_date', 'status']
        widgets = {
            'visit_start_date': DateInput(attrs={'type': 'date'}),
            'visit_end_date': DateInput(attrs={'type': 'date'}),
            'term_start_date': DateInput(attrs={'type': 'date'}),
            'term_end_date': DateInput(attrs={'type': 'date'}),
            'coa_approval_date': DateInput(attrs={'type': 'date'}),
            'term_comment':forms.Textarea(attrs={'rows': 1 }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.filter(active=True)


class SchoolInfoForApplicationForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name', 'phone_number', 'email','website',
            'principal', 'date_hired', 'principal_phone', 'principal_email',
            'board_chair', 'board_chair_phone', 'board_chair_email',
            'year_school_started','school_type_choice',
        ]
        widgets = {
            'school_type_choice': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'website':
                field.required = True
            else:
                field.required = False

class AccreditationApplicationForm(forms.ModelForm):
    class Meta:
        model = AccreditationApplication
        exclude = ['school', 'ss_orientation_date', 'site_visit_start_date', 'site_visit_end_date' ]

        widgets = {
            'lowest_grade': forms.TextInput(attrs={'class': 'zip-code-input', 'maxlength': '5'}),
            'current_highest_grade': forms.TextInput(attrs={'class': 'zip-code-input', 'maxlength': '5'}),
            'planned_highest_grade': forms.TextInput(attrs={'class': 'zip-code-input', 'maxlength': '5'}),
            'date': forms.DateInput(attrs={'class': '', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = True

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_1', 'city', 'state_us', 'zip_code', 'country']

        widgets = {
            'address_1': forms.TextInput(attrs={'class': 'address-1-input'}),
            'city': forms.TextInput(attrs={'class': 'city-input'}),
            'zip_code': forms.TextInput(attrs={'class': 'zip-code-input'}),
            'country': forms.Select(attrs={}),
            'state_us': forms.Select(attrs={}),
        }

class AccreditationApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = AccreditationApplication
        fields = ['ss_orientation_date', 'site_visit_start_date', 'site_visit_end_date']
        widgets = {
            'ss_orientation_date': forms.DateInput(attrs={'type': 'date'}),
            'site_visit_start_date': forms.DateInput(attrs={'type': 'date'}),
            'site_visit_end_date': forms.DateInput(attrs={'type': 'date'}),
        }