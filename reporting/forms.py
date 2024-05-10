from django import forms
from reporting.models import Student
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    file = forms.FileField()

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('annual_report', 'id', 'age_at_registration')
        widgets = {
            'name': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'address': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'us_state': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'TN_county': forms.Select(attrs={'style': 'max-width: 100px;'}),
            'country': forms.Select(attrs={'style': 'max-width: 100px;'}),  # forms.Select for foreign key
            'birth_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
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
        if 'us_state' in self.fields:
            student_country = cleaned_data.get('country')
            us_state = cleaned_data.get('us_state')
            if student_country:
                if student_country.code == 'US' and not us_state:
                    self.add_error('us_state', ValidationError("required for US address"))
        if 'TN_county' in self.fields:
            us_state = cleaned_data.get('us_state')
            TN_county=cleaned_data.get('TN_county')
            if us_state == 'TN' and not TN_county:
                self.add_error('TN_county', ValidationError("required for TN students"))
            if us_state != 'TN' and TN_county:
                self.add_error('TN_county', ValidationError("only for TN students"))

        return cleaned_data
