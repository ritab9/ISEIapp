from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import inlineformset_factory
# from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from django.forms.models import BaseInlineFormSet
from .models import *


class PDAreportForm(ModelForm):
    class Meta:
        model = PDAReport
        fields = ('school_year', 'date_submitted', 'summary', 'principal_comment', 'isei_comment',)
        widgets = {
        #    'school_year': forms.TextInput(attrs={'class': 'form-controls', 'placehoder': 'Enter school year'}),
        #    'date_submitted': forms.DateField(attrs={'class': 'form-controls', 'placehoder': 'Enter date'}),
             'summary': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter summary for combined activities', 'rows':10}),
             'principal_comment': forms.Textarea(
                attrs={'class': 'form-controls','rows':4 }),
            'isei_comment': forms.Textarea(
                attrs={'class': 'form-controls', 'rows': 4 }),
            'date_submitted': forms.DateInput(format ='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
        }



class PDAInstanceForm(ModelForm):
    class Meta:
        model = PDAInstance
        fields = ('pda_type','description', 'date_completed', 'units', 'amount', 'file', 'date_resubmitted')
        widgets = {
            'file': forms.FileInput(attrs={'size': 1}),
            'date_completed': forms.DateInput (format ='%m/%d/%Y', attrs = {'placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
            'amount': forms.NumberInput (attrs={'style':'width:60px' }),
        }


PDAInstanceFormSet = inlineformset_factory(PDAReport, PDAInstance, form=PDAInstanceForm, extra=1,
                                           can_delete=False)

class AcademicClassForm(ModelForm):
    class Meta:
        model = AcademicClass
        fields = ('university','class_name', 'date_completed', 'transcript_requested', 'transcript_received')
        widgets = {
            'date_completed': forms.DateInput (format ='%m/%d/%Y', attrs = {'placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
        }


AcademicClassFormSet = inlineformset_factory(PDAReport, AcademicClass, form=AcademicClassForm, extra=1,
                                           can_delete=False)


class TCertificateForm(ModelForm):
    class Meta:
        model=TCertificate
        fields =('__all__')

TEndorsementFormSet = inlineformset_factory(TCertificate, TEndorsement, fields=('endorsement',), extra=1)




#Not Used at the moment
#to be used by ISEI staff to add the approved CEUs and individual deny instances as needed
#PDAInstanceFormSetNoExtraRows = inlineformset_factory(PDAReport, PDAInstance, form=PDAInstanceForm, extra=0,
#                                           can_delete=False)

#class PDAInstanceFormSetHelper(FormHelper):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.form_method = 'post'
#        self.layout = Layout(
#            'pda_type',
#            'description','date_completed',
#            'pages', 'amount', 'ceu', 'file'
#        )
#        self.render_required_fields = True


#class DocumentForm(forms.Form): #unused but keeping it just in case
#    name = forms.CharField(max_length=35, min_length=1)
#    docfile = forms.FileField(
#        label='Select a file',
#        help_text='max. 42 megabytes'
#    )

