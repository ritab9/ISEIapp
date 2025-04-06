from django.forms import ModelForm
from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from teachercert.models import *



class CEUReportForm(ModelForm):
    class Meta:
        model = CEUReport
        fields = ('date_submitted', 'summary', 'principal_comment', 'isei_comment',)
        widgets = {
        #    'school_year': forms.TextInput(attrs={'class': 'form-controls', 'placehoder': 'Enter school year'}),
             'summary': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter summary for combined activities', 'rows':10}),
             'principal_comment': forms.Textarea(
                attrs={'class': 'form-controls','rows':4 }),
            'isei_comment': forms.Textarea(
                attrs={'class': 'form-controls', 'rows': 4 }),
            'date_submitted': forms.TextInput(attrs={'placeholder': 'mm/dd/yyyy', 'type':'date'}),
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
            #'ceu_category': forms.Select ('label':'CEU Category'}),
            #'ceu_type': forms.Select(attrs={'label': 'CEU Type'}),
            'file': forms.FileInput(attrs={'size': 1}),
            'date_completed': forms.TextInput (attrs = {'type':'date','placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
            'amount': forms.NumberInput (attrs={'style':'width:60px' }),
            'description': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Activity Description', 'rows': 1}),
            'evidence': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Activity Description', 'rows': 1}),
        }


#not used
CEUInstanceFormSet = inlineformset_factory(CEUReport, CEUInstance, form=CEUInstanceForm, extra=1,
                                           can_delete=False)


class BulkCEUForm(forms.Form):
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False)
    school_year = forms.ModelChoiceField(queryset=SchoolYear.objects.filter(active_year=True), required=True)
    ceu_type = forms.ModelChoiceField(queryset=CEUType.objects.filter(ceu_category__name__in=["Collaboration", "Group"]), required=True)
    description = forms.CharField(
                                  required=True)
    approved_ceu = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    date_completed = forms.DateField(required=True)
    evidence = forms.CharField(required=False)
    file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        self.teachers = kwargs.pop('teachers', [])
        is_principal = kwargs.pop('is_principal', False)  # Pass this from the view
        super().__init__(*args, **kwargs)
        if is_principal:
            self.fields.pop('school')
        for teacher in self.teachers:
            self.fields[f'approved_ceu_{teacher.id}'] = forms.DecimalField(
                max_digits=5, decimal_places=2, required=False,
                initial= 0
            )

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
            'date_completed': forms.TextInput ( attrs = {'type':'date','placeholder':'mm/dd/yyyy', 'style':'width:130px' }),
        }

class TCertificateForm(ModelForm):
    class Meta:
        model=TCertificate
        fields =('__all__')
        widgets = {
            'issue_date': forms.TextInput( attrs={'type':'date','placeholder': 'mm/dd/yyyy'}),
            'renewal_date': forms.TextInput(attrs={'type':'date','placeholder': 'mm/dd/yyyy'}),
            'renewal_requirements': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2,}),
            'public_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2}),
            'office_note': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Enter renewal requirements', 'rows': 2}),
        }


class TEndorsementForm(forms.ModelForm):
    class Meta:
        model = TEndorsement
        fields = ('endorsement', 'range')
        widgets = {
            'range':forms.Textarea(attrs={'rows':1,'cols':5}),
        }


TEndorsementFormSet = inlineformset_factory(TCertificate, TEndorsement, form=TEndorsementForm,  extra = 3, can_delete=True)


class TeacherBasicRequirementForm (forms.ModelForm):
    class Meta:
        model= TeacherBasicRequirement
        fields = ('basic_requirement','met','course')

TeacherBasicRequirementFormSet = modelformset_factory(TeacherBasicRequirement, form = TeacherBasicRequirementForm, extra=0)


class TeacherCertificationApplicationForm(ModelForm):
    class Meta:
        model = TeacherCertificationApplication
        fields =('cert_level','endors_level','courses_taught',
                 'resume_file','principal_letter_file',
                 'felony','felony_description','sexual_offence','sexual_offence_description',
                 'signature', 'date')
        widgets = {
            'courses_taught': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Courses Taught','rows':1}),
            'felony_description': forms.Textarea(
                attrs={'class': 'form-controls', 'placehoder': 'Felony Description', 'rows': 10}),
            'sexual_offence_description': forms.Textarea(
                attrs = {'class': 'form-controls', 'placehoder': 'Sexual Offence Description', 'rows': 10}),
            'date': forms.TextInput(attrs={'placeholder': 'mm/dd/yyyy'}),
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

            'isei_revision_date': forms.TextInput(
                attrs={'placeholder': 'mm/dd/yyyy', 'type':'date'}),
        }

class StandardChecklistForm(ModelForm):
    class Meta:
        model = StandardChecklist
        exclude=['teacher',]
        widgets = {
            'sda_education':forms.NumberInput(attrs = {'size': 3,}),
            'psychology': forms.NumberInput (attrs={'size': 3}),
            'dev_psychology': forms.NumberInput (attrs={'size': 3}),
            'assessment': forms.NumberInput(attrs={'size': 3}),
            'exceptional_child': forms.NumberInput(attrs={'size': 3}),
            'technology': forms.NumberInput(attrs={'size': 3}),
            'sec_methods': forms.NumberInput(attrs={'size': 3}),
            'sec_rw_methods': forms.NumberInput(attrs={'size': 3}),
            'credits18': forms.Textarea(attrs={'rows': 1}),
            'credits12': forms.Textarea(attrs={'rows': 1}),

            'em_science': forms.NumberInput(attrs={'size': 3}),
            'em_math': forms.NumberInput(attrs={'size': 3}),
            'em_reading': forms.NumberInput(attrs={'size': 3}),
            'em_language': forms.NumberInput(attrs={'size': 3}),
            'em_religion': forms.NumberInput(attrs={'size': 3}),
            'em_social': forms.NumberInput(attrs={'size': 3}),
            'em_health': forms.NumberInput(attrs={'size': 3}),
            'other_ed_credit': forms.NumberInput(attrs={'size': 3}),

        }