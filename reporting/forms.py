from django import forms
from reporting.models import Student, Day190, Vacations, InserviceDiscretionaryDays, AbbreviatedDays, Inservice
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import Country, TNCounty
from .models import AnnualReport


class UploadFileForm(forms.Form):
    file = forms.FileField()


class StudentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        annual_report_id = kwargs.pop('annual_report_id', None)
        super(StudentForm, self).__init__(*args, **kwargs)
        if annual_report_id is not None:
            annual_report = AnnualReport.objects.get(id=annual_report_id)
            preferential_countries = list(Country.objects.filter(student__annual_report=annual_report).distinct())
            other_countries = list(Country.objects.exclude(id__in=[country.id for country in preferential_countries]))
            self.fields['country'].choices = [(country.id, country.name) for country in
                                              preferential_countries + other_countries]


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


class Day190Form(forms.ModelForm):
    class Meta:
        model = Day190
        exclude = ['id','annual_report']

        widgets = {
            'start_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'number_of_sundays': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
            'number_of_days': forms.NumberInput(attrs={'min': 1, 'max': 250, 'style': 'max-width: 30px; border:none'}),
            'inservice_days': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
        }


class VacationsForm(forms.ModelForm):
    class Meta:
        model = Vacations
        exclude = ['id','day190']

        widgets = {
            'name': forms.TextInput(attrs={'style': 'max-width: 300px;'}),
            'start_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'weekdays': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
        }

class InserviceDiscretionaryDaysForm(forms.ModelForm):
    TYPE_CHOICES = [
        (None, '--------------'),
        ('CI', 'Curriculum Improvement'),
        ('II', 'Instructional Improvement'),
        ('CM', 'Classroom Management'),
        ('TE', 'Teacher/Administrator Evaluation'),
        ('TC', 'Teacher Convention'),
        ('OT', 'Other'),
        ('DS', 'Discretionary'),
    ]

    type = forms.ChoiceField(choices=TYPE_CHOICES, required=True)

    class Meta:
        model = InserviceDiscretionaryDays
        exclude = ['id', 'day190']

        widgets = {
            'date': forms.TextInput(attrs={'style': 'max-width: 150px;'}),
            'hours': forms.NumberInput(attrs={'min': 1, 'max': 40, 'style': 'max-width: 30px;'}),
        }


class AbbreviatedDaysForm(forms.ModelForm):
    class Meta:
        model = AbbreviatedDays
        exclude = ['id','day190']

        widgets = {
            'date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'hours': forms.NumberInput(attrs={'min': 1, 'max': 8, 'style': 'max-width: 30px;'}),
        }

class InserviceForm(forms.ModelForm):
    class Meta:
        model = Inservice
        fields = ['dates', 'topic', 'presenter', 'hours']
        #exclude=['id','annual_report']

        widgets = {
            'hours': forms.NumberInput(attrs={'min': 1, 'style': 'max-width: 30px;', 'class':'hours-input'}),
        }
