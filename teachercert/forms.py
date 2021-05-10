from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import inlineformset_factory
# from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from django.forms.models import BaseInlineFormSet
from .models import *


class PDARecordForm(ModelForm):
    class Meta:
        model = PDARecord
        fields = ('school_year', 'date_submitted', 'summary')
        widgets = {
        #    'school_year': forms.TextInput(attrs={'class': 'form-controls', 'placehoder': 'Enter school year'}),
        #    'date_submitted': forms.DateField(attrs={'class': 'form-controls', 'placehoder': 'Enter date'}),
             'summary': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter summary for combined activities'})
        }


class PDAInstanceForm(ModelForm):
    class Meta:
        model = PDAInstance
        fields = ('pda_type','description', 'date_completed',  'pages', 'clock_hours', 'ceu', 'file')
        widgets = {
            'file': forms.FileInput(attrs={'size': 1}),
        }


PDAInstanceFormSet = inlineformset_factory(PDARecord, PDAInstance, form=PDAInstanceForm, extra=1,
                                           can_delete=False)

#class PDAInstanceFormSetHelper(FormHelper):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.form_method = 'post'
#        self.layout = Layout(
#            'pda_type',
#            'description','date_completed',
#            'pages', 'clock_hours', 'ceu', 'file'
#        )
#        self.render_required_fields = True



class DocumentForm(forms.Form): #unused but keeping it just in case
    name = forms.CharField(max_length=35, min_length=1)
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

