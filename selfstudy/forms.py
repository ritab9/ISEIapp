from django import forms
from django.forms import modelformset_factory

from .models import *


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['school_history']  # Add fields you want to display in the form

class FinancialTwoYearDataEntriesForm(forms.ModelForm):
    class Meta:
        model = FinancialTwoYearDataEntries
        fields = ['two_years_ago', 'one_year_ago']
        labels = { 'two_years_ago': 'Two Years Ago', 'one_year_ago': 'One Year Ago',}

class FinancialAdditionalDataEntriesForm(forms.ModelForm):
    class Meta:
        model = FinancialAdditionalDataEntries
        fields = ['value']
        labels = { 'value': 'Value'}

FinancialTwoYearDataFormSet = modelformset_factory(FinancialTwoYearDataEntries,form=FinancialTwoYearDataEntriesForm, extra=0)
FinancialAdditionalDataFormSet = modelformset_factory(FinancialAdditionalDataEntries,form=FinancialAdditionalDataEntriesForm, extra=0)

from django import forms
import json
from .models import IndicatorEvaluation


class IndicatorEvaluationForm(forms.ModelForm):
    class Meta:
        model = IndicatorEvaluation
        fields = ['score', 'reference_documents', 'explanation']
        widgets = {
            'reference_documents': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }


IndicatorEvaluationFormSet = forms.modelformset_factory(
    IndicatorEvaluation,
    form=IndicatorEvaluationForm,
    extra=0,  # No additional empty forms
)
