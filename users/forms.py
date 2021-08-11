from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from captcha.fields import CaptchaField
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout
from django.forms.models import BaseInlineFormSet
from .models import *


class CreateUserForm(UserCreationForm):
    captcha = CaptchaField()
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'captcha']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'size': 1}),
            'date_of_birth': forms.DateInput( format ='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy', 'input-formats':'%m/%d/%Y'}),
        }


