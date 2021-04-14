from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout
from django.forms.models import BaseInlineFormSet
from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

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
        }


