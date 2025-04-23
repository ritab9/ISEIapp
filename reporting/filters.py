from django import forms
from .models import Student, StaffStatus, StaffPosition, Degree, Subject
from users.models import Country, TNCounty, StateField, School


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
        if annual_report and annual_report.school and annual_report.school.street_address.country and annual_report.school.street_address.country.code == 'US':
            self.fields['us_state'] = forms.ChoiceField(choices=[('', '---------')] + list(StateField.STATE_CHOICES),
                                                        required=False)

            if annual_report.school.street_address.state_us == 'TN':
                self.fields['TN_county'] = forms.ModelChoiceField(queryset=TNCounty.objects.all(), required=False)


#used on the ISEI personnel_directory
class EmployeeFilterForm(forms.Form):
    school = forms.ModelChoiceField(queryset=School.objects.filter(active=True,), required=False)
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '15'}))
    status = forms.ChoiceField(choices=[('', 'All')] + list(StaffStatus.choices), required=False)
    position = forms.ModelChoiceField(queryset=StaffPosition.objects.all(), required=False)
    degree = forms.ModelChoiceField(queryset=Degree.objects.all(), required=False)
    subjects_teaching = forms.ModelChoiceField(queryset=Subject.objects.all(), required=False)

#used on school_personnel_directory (the public directory)
class PersonnelFilterForm(forms.Form):
    school = forms.ModelChoiceField(queryset=School.objects.filter(active=True), required=False)
    name = forms.CharField(max_length=100, required=False)

    position = forms.ChoiceField(
        choices=[('', '---------')] + [
            (name, name) for name in StaffPosition.objects.order_by().values_list('name', flat=True).distinct()
        ],
        required=False
    )

    subject = forms.ChoiceField(
        choices=[('', '---------')] + [
            (name, name) for name in Subject.objects.order_by().values_list('name', flat=True).distinct()
        ],
        required=False
    )