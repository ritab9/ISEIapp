from django import forms
from reporting.models import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from users.models import Country, TNCounty
from .models import *
from django.forms import BaseModelFormSet, TextInput, NumberInput, DateInput
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory

from django.forms.widgets import CheckboxSelectMultiple



class UploadFileForm(forms.Form):
    file = forms.FileField()

def my_formset_factory(model, form, extra, can_delete, exclude, is_us_school, is_tn_school, school):
    class _StudentForm(form):  # This way `form` parameter used
        def __init__(self, *args, **kwargs):
            super().__init__(is_us_school=is_us_school, is_tn_school=is_tn_school, school=school, *args, **kwargs)

    return modelformset_factory(model=model, form=_StudentForm, extra=extra, can_delete=can_delete, exclude=exclude)


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.is_us_school = kwargs.pop('is_us_school', False)
        self.is_tn_school = kwargs.pop('is_tn_school', False)
        self.school = kwargs.pop('school', None)

        super().__init__(*args, **kwargs)

        if self.school:
            self.fields['grade_level'].choices = [(None, '-----')] + self.school.get_allowed_grade_choices()

        # Modify parent_sda choices to include only 'Y', 'N', and 'U'
        self.fields['parent_sda'].choices = [('Y', 'Yes, SDA'),('N', 'No'), ('U', '-'),]

    class Meta:
        model = Student
        #exclude = ('annual_report', 'id', 'age_at_registration')
        fields=( 'name', 'grade_level', 'status', 'registration_date', 'withdraw_date',  'birth_date', 'age', 'gender', 'boarding', 'location', 'address', 'us_state', 'TN_county', 'country',  'boarding', 'baptized',
                'parent_sda')
        field_order = ( 'name', 'grade_level', 'status', 'registration_date', 'withdraw_date',  'birth_date', 'age', 'gender', 'boarding', 'location', 'address', 'us_state', 'TN_county', 'country',  'boarding', 'baptized',
                'parent_sda')

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

        age = cleaned_data.get("age")
        birth_date = cleaned_data.get("birth_date")
        if not (age or birth_date):
            raise forms.ValidationError(
                "Student must have either their age at registration or a birth date entered."
            )

        gender = cleaned_data.get('gender')
        if gender == 'U':
            self.add_error('gender', ValidationError("Select Gender."))


        if self.is_us_school:
            country = cleaned_data.get('country')
            if country and country.code == 'US':
                us_state = cleaned_data.get('us_state')
                if not us_state:
                    self.add_error('us_state', ValidationError("Required for US address"))
                if self.is_tn_school:
                    tn_county = cleaned_data.get('TN_county')
                    if us_state == 'TN' and not tn_county:
                        self.add_error('TN_county', ValidationError("Required for TN students"))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.withdraw_date:
            instance.status = 'withdrawn'
        if commit:
            instance.save()
        return instance



#Day 190 Forms
class Day190Form(forms.ModelForm):
    class Meta:
        model = Day190
        exclude = ['id','annual_report']

        widgets = {
            'start_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            #'number_of_sundays': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
            'number_of_days': forms.NumberInput(attrs={'min': 1, 'max': 250, 'style': 'max-width: 30px; border:none'}),
            'inservice_days': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
            'file': forms.FileInput(attrs={'size': 1}),
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
        ('IS', 'ISEI Workshop'),
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
            'dates': forms.TextInput(attrs={'style': 'max-width: 150px;'}),
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

class SundaySchoolDaysForm(forms.ModelForm):
    class Meta:
        model = SundaySchoolDays
        fields = ['date', 'type']

        widgets = {
            'date': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date.weekday() != 6:  # as Python's weekday function returns 0 for Monday and 6 for Sunday
            raise ValidationError("The selected date does not fall on a Sunday.")
        return date

class BaseSundaySchoolDaysFormSet(BaseModelFormSet):

    def clean(self):
        """Checks that no two days have the same date."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        dates = []
        for form in self.forms:
            if form.is_valid() and form.cleaned_data and 'date' in form.cleaned_data:
                date = form.cleaned_data.get('date')
                if date in dates:
                    raise forms.ValidationError("Dates must be unique.")
                dates.append(date)


class EducationalEnrichmentActivityForm(forms.ModelForm):
    class Meta:
        model = EducationalEnrichmentActivity
        fields = ['type', 'dates', 'days']

        widgets = {
            'days': forms.NumberInput(attrs={'min': 1, 'max': 20, 'style': 'max-width: 30px;'}),
            'dates': forms.TextInput(attrs={'style': 'max-width: 150px;'}),

        }

#Inservice Form
class InserviceForm(forms.ModelForm):
    class Meta:
        model = Inservice
        fields = ['dates', 'topic', 'presenter', 'hours']

        widgets = {
            'hours': forms.NumberInput(attrs={'min': 1, 'style': 'max-width: 30px;', 'class':'hours-input'}),
        }

#Employee Forms

class PersonnelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        schoolID = kwargs.pop('schoolID', None)
        super().__init__(*args, **kwargs)

        if schoolID is not None:
            queryset = Teacher.objects.filter(user__profile__school_id=schoolID, user__is_active=True).select_related('user')
            self.fields['teacher'].queryset = queryset


    class Meta:
        model = Personnel
        fields = ['first_name', 'last_name', 'gender', 'status', 'teacher',
                  'years_administrative_experience', 'years_teaching_experience', 'years_work_experience', 'years_at_this_school', 'email_address', 'phone_number', 'sda',
                  'positions', 'subjects_teaching', 'subjects_taught']


PersonnelDegreeFormset = inlineformset_factory(
    Personnel,
    PersonnelDegree,
    fields=('degree', 'area_of_study'),
    extra=1,
    can_delete=True,
)

from django import forms
from .models import Closing


class ClosingForm(forms.ModelForm):
    class Meta:
        model = Closing
        fields = [
                  'final_school_day', 'no_mission_trips',
                  'no_mission_trips_school',
                  'mission_trip_locations',
                  'student_lead_evangelistic_meetings',
                  'evangelistic_meeting_locations',
                  'student_evangelistic_meetings_baptism',
                  'student_baptism_sda_parent',
                  'student_baptism_non_sda_parent',
                  'outreach']

        widgets = {
             'final_school_day': forms.DateInput(attrs={'style': 'max-width: 300px;', 'type': 'date'}),
            'no_mission_trips': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
            'no_mission_trips_school': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
            'mission_trip_locations': TextInput(attrs={'style': 'max-width: 300px;'}),
            'student_lead_evangelistic_meetings': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
            'evangelistic_meeting_locations': TextInput(attrs={'style': 'max-width: 300px;'}),
            'student_evangelistic_meetings_baptism': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
            'student_baptism_sda_parent': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
            'student_baptism_non_sda_parent': forms.NumberInput(attrs={'min': 1, 'max': 999, 'style': 'max-width: 30px;'}),
        }

from decimal import Decimal, InvalidOperation

class CommaSeparatedDecimalField(forms.DecimalField):
    def clean(self, value):
        if value is not None:
            print(value)
            value = str(value).replace(',', '')  # Remove commas
        return super().clean(value)

class WorthyStudentScholarshipForm(forms.ModelForm):
    school_generated_fund = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )
    wss_fund = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )
    next_year_budget = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )


    class Meta:
            model = WorthyStudentScholarship
            fields = [
                      'school_generated_fund', 'wss_fund',
                        'students_assisted_total', 'students_assisted_wss',
                        'next_year_budget', 'letter'
                      ]

            widgets = {
                #'school_generated_fund': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
                #'wss_fund': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
                'students_assisted_total': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
                'students_assisted_wss': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
                #'next_year_budget': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
                'letter': forms.FileInput(attrs={'size': 1}),

            }

class WorthyStudentScholarshipNonMemberForm(forms.ModelForm):
    school_generated_fund = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )
    wss_fund = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )
    next_year_budget = CommaSeparatedDecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.TextInput(attrs={'style': 'max-width: 100px;'})
    )

    class Meta:
        model = WorthyStudentScholarship
        fields = [
            'opening_enrollment', 'closing_enrollment',
            'school_generated_fund', 'wss_fund',
            'students_assisted_total', 'students_assisted_wss',
            'next_year_budget', 'letter'
            ]

        widgets = {
            'opening_enrollment': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
            'closing_enrollment': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
            'students_assisted_total': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
            'students_assisted_wss': forms.NumberInput(attrs={'style': 'max-width: 100px;'}),
            'letter': forms.FileInput(attrs={'size': 1}),

        }


"""class EnrollmentForm(forms.Form):

    # Dynamically create fields for each grade level in the school's range
    def __init__(self, *args, **kwargs):
        allowed_grades = kwargs.pop('allowed_grades', [])
        super().__init__(*args, **kwargs)

        for grade in allowed_grades:
            self.fields[f'enrollment_count_{grade}'] = forms.IntegerField(
                label=f"Grade {grade}", min_value=0, initial=0, required=True) """