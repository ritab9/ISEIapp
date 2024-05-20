from django import forms
from .models import Student
from users.models import Country, TNCounty, StateField

class StudentFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        annual_report = kwargs.pop('annual_report', None)
        super(StudentFilterForm, self).__init__(*args, **kwargs)

        grade_level_choices = [('', '---------')] + list(Student.GRADE_LEVEL_CHOICES)
        status_choices = [('', '---------')] + list(Student.STATUS_CHOICES)
        location_choices = [('', '---------')] + list(Student.LOCATION_CHOICES)

        self.fields['grade_level'] = forms.ChoiceField(choices=grade_level_choices, required=False)
        self.fields['status'] = forms.ChoiceField(choices=status_choices, required=False)
        self.fields['location'] = forms.ChoiceField(choices=location_choices, required=False)
        self.fields['gender'] = forms.ChoiceField(choices=[('', '---------')] + list(Student.GENDER_CHOICES),
                                                  required=False)
        self.fields['country'] = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)

        # Check the properties of the annual report
        if annual_report and annual_report.school and annual_report.school.address.country and annual_report.school.address.country.code == 'US':
            self.fields['us_state'] = forms.ChoiceField(choices=[('', '---------')] + list(StateField.STATE_CHOICES),
                                                        required=False)

            if annual_report.school.address.state_us == 'TN':
                self.fields['TN_county'] = forms.ModelChoiceField(queryset=TNCounty.objects.all(), required=False)
