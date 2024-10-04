from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
# from captcha.fields import CaptchaField
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout
from django.forms.models import BaseInlineFormSet
from .models import *
from localflavor.us.forms import USStateField
from teachercert.models import SchoolYear

class SchoolYearForm(forms.Form):
    school_year = forms.ModelChoiceField(
        queryset=SchoolYear.objects.filter(active_year=True),
        empty_label=None,
        widget=forms.Select(attrs={'id': 'schoolYearDropdown','width': '150px' }),
    )

class CreateUserForm(UserCreationForm):
    #captcha = CaptchaField()
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', ]

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user','joined_at', 'profile_picture',]
        widgets = {
            # 'profile_picture': forms.FileInput(attrs={'size': 1}),
            'date_of_birth': forms.DateInput( format ='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy', 'input-formats':'%m/%d/%Y'}),
        }

class SchoolAddressForm(ModelForm):
    class Meta:
        model = Address
        fields =('__all__')
        exclude = ('teacher',)


class TeacherAddressForm(ModelForm):
    class Meta:
        model = Address
        fields =('__all__')
        exclude = ('school',)



class SchoolOfEmploymentForm(ModelForm):
    class Meta:
        model = SchoolOfEmployment
        fields = '__all__'
        exclude = ['teacher', 'id']
        widgets = {
            'start_date': forms.DateInput(format='%m/%d/%Y',
                                             attrs={'placeholder': 'yyyy'}),
            'end_date': forms.DateInput(format='%m/%d/%Y',
                                            attrs={'placeholder': 'yyyy or to date'}),
        }


SchoolOfEmploymentFormSet = inlineformset_factory(Teacher, SchoolOfEmployment, form = SchoolOfEmploymentForm, extra=5, can_delete=True)

class CollegeAttendedForm(ModelForm):
    class Meta:
        model = CollegeAttended
        fields = '__all__'
        exclude = ['teacher', 'id' ]
        widgets = {
            'start_date': forms.Textarea(attrs={'rows':1, 'cols':4, 'placeholder': 'yyyy',}),
            'end_date': forms.Textarea(attrs={'rows':1, 'cols':4,'placeholder': 'yyyy', }),
            'transcript_received': forms.HiddenInput(),
        }

CollegeAttendedFormSet = inlineformset_factory(Teacher, CollegeAttended, form = CollegeAttendedForm, extra=5, can_delete=True)

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ('__all__')
        exclude =['id',]

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'phone_number', 'website', 'principal', 'president', 'textapp', 'type', 'fire_marshal_date','initial_accreditation_date']
        widgets = {
            'fire_marshal_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SchoolAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_1', 'address_2', 'city', 'state_us', 'zip_code', 'country']
