from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
# from captcha.fields import CaptchaField
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout
from django.forms.models import BaseInlineFormSet
from .models import *
from localflavor.us.forms import USStateField


class CreateUserForm(UserCreationForm):
    #captcha = CaptchaField()
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', ]


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user','joined_at', 'profile_picture']
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
                                             attrs={'placeholder': 'mm/dd/yyyy', 'input-formats': '%m/%d/%Y'}),
            'end_date': forms.DateInput(format='%m/%d/%Y',
                                            attrs={'placeholder': 'mm/dd/yyyy or to date', 'input-formats': '%m/%d/%Y'}),
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