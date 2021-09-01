from django.forms import ModelForm, modelformset_factory, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
# from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from django.forms.models import BaseInlineFormSet
from teachercert.models import *




class CEUreportForm(ModelForm):
    class Meta:
        model = CEUReport
        fields = ('school_year', 'date_submitted', 'summary', 'principal_comment', 'isei_comment',)
        widgets = {
        #    'school_year': forms.TextInput(attrs={'class': 'form-controls', 'placehoder': 'Enter school year'}),
             'summary': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter summary for combined activities', 'rows':10}),
             'principal_comment': forms.Textarea(
                attrs={'class': 'form-controls','rows':4 }),
            'isei_comment': forms.Textarea(
                attrs={'class': 'form-controls', 'rows': 4 }),
            'date_submitted': forms.DateInput(format ='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
        }


class CEUInstanceForm(ModelForm):
    # Ajax
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ceu_type'].queryset = CEUType.objects.none()

        if 'ceu_category' in self.data:
            try:
                ceu_category_id = int(self.data.get('ceu_category'))
                self.fields['ceu_type'].queryset = CEUType.objects.filter(ceu_category_id=ceu_category_id).order_by(
                    'description')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['ceu_type'].queryset = self.instance.ceu_category.ceutype_set.all()

    class Meta:
        model = CEUInstance
        fields = ('ceu_category', 'ceu_type','description', 'date_completed', 'units', 'amount', 'evidence', 'file', 'date_resubmitted')
        widgets = {
            #'ceu_category': forms.Select (attrs={'class':'category_class'}),
            #'ceu_type': forms.Select(attrs={'class': 'type_class'}),
            'file': forms.FileInput(attrs={'size': 1}),
            'date_completed': forms.DateInput (format ='%m/%d/%Y', attrs = {'placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
            'amount': forms.NumberInput (attrs={'style':'width:60px' }),
            'description': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Activity Description', 'rows': 1}),
            'evidence': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Activity Description', 'rows': 1}),
        }



CEUInstanceFormSet = inlineformset_factory(CEUReport, CEUInstance, form=CEUInstanceForm, extra=1,
                                           can_delete=False)

#not used
class RenewalForm(forms.ModelForm):
    class Meta:
        model = Renewal
        fields =('name', 'description')
        widgets ={ 'description': forms.Textarea() }

class AcademicClassForm(ModelForm):
    class Meta:
        model = AcademicClass
        fields = ('__all__')
        widgets = {
            'date_completed': forms.DateInput (format ='%m/%d/%Y', attrs = {'placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
        }

class TCertificateForm(ModelForm):
    class Meta:
        model=TCertificate
        fields =('__all__')
        widgets = {
            'issue_date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
            'renewal_date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
            'renewal_requirements': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2}),
            'public_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2}),
            'office_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2}),
        }

TEndorsementFormSet = inlineformset_factory(TCertificate, TEndorsement, fields=('endorsement',), extra = 3)


class TeacherBasicRequirementForm (forms.ModelForm):
    class Meta:
        model= TeacherBasicRequirement
        fields = ('met',)

TeacherBasicRequirementFormSet = modelformset_factory(TeacherBasicRequirement, form = TeacherBasicRequirementForm, extra=0)


class TeacherCertificationApplicationForm(ModelForm):
    class Meta:
        model = TeacherCertificationApplication
        fields =('cert_level','endors_level','courses_taught',
                 'resume_file','principal_letter_file',
                 'felony','felony_description','sexual_offence','sexual_offence_description',
                 'signature', 'date')
        widgets = {
            'felony_description': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Felony Description', 'rows': 10}),
            'sexual_offence_description': forms.Textarea(
                attrs = {'class': 'form-controls', 'placehoder': 'Sexual Offence Description', 'rows': 10}),
            'date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
            'file': forms.FileInput(attrs={'size': 1}),
        }

class TeacherCertificationApplicationISEIForm(ModelForm):
    class Meta:
        model = TeacherCertificationApplication
        fields = ['public_note', 'isei_note', 'billed', 'closed', 'isei_revision_date']
        widgets = {
            'public_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Note visible to the teacher and principal', 'rows': 2}),
            'isei_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Office use only', 'rows': 2}),

            'isei_revision_date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
        }
