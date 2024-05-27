from django import forms
from reporting.models import Student
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import Country, TNCounty
from django.core.cache import cache, caches


class UploadFileForm(forms.Form):
    file = forms.FileField()


class StudentForm(forms.ModelForm):


    class Meta:
        model = Student
        #exclude = ('annual_report', 'id', 'age_at_registration')
        fields=('name', 'gender', 'address', 'us_state', 'TN_county', 'country', 'birth_date','age', 'grade_level', 'baptized','parent_sda',
                'status', 'registration_date','withdraw_date', 'location')
        field_order = ( 'name', 'gender', 'address', 'us_state', 'TN_county', 'country', 'birth_date', 'age', 'grade_level', 'boarding', 'baptized',
                'parent_sda', 'status', 'registration_date', 'withdraw_date', 'location')

        widgets = {
            'name': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'address': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'us_state': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'TN_county': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'country': forms.Select(attrs={'style': 'width: 100px;'}),  # forms.Select for foreign key
            'birth_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'age': forms.NumberInput (attrs={'min': 1, 'max': 110, 'style': 'max-width: 30px;'}),
            'baptized': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'parent_sda': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'status': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for choices field
            'grade_level': forms.Select(attrs={'style': 'max-width: 50px;'}),
            'registration_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'withdraw_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'location': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for choices field
        }

    def clean(self):
        cleaned_data = super().clean()

        country = cleaned_data.get('country')
        TN_county = cleaned_data.get('TN_county')

        if country and country.code == 'US':
            us_state = cleaned_data.get('us_state')
            if not us_state:
                self.add_error('us_state', ValidationError("required for US address"))

            if us_state=='TN' and not TN_county:
                self.add_error('TN_county', ValidationError("required for TN students"))


        return cleaned_data
