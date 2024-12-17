from django import forms
from django.forms import DateInput
from .models import Accreditation
from users.models import School


class AccreditationForm(forms.ModelForm):
    class Meta:
        model = Accreditation
        fields = ['school', 'visit_start_date', 'visit_end_date','term', 'term_start_date', 'term_end_date', 'current_accreditation']
        widgets = {
            'visit_start_date': DateInput(attrs={'type': 'date'}),
            'visit_end_date': DateInput(attrs={'type': 'date'}),
            'term_start_date': DateInput(attrs={'type': 'date'}),
            'term_end_date': DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.filter(active=True)