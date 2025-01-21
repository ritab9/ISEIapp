from django import forms
from django.forms import modelformset_factory, inlineformset_factory

from .models import *
from apr.models import ActionPlan, ActionPlanSteps


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

class StandardEvaluationForm(forms.ModelForm):
    class Meta:
        model = StandardEvaluation
        fields = ['narrative', 'average_score']  # Include only narrative and average_score fields

        widgets = {
            'narrative': forms.Textarea(attrs={'rows': 2}),
            'average_score': forms.HiddenInput(),
        }

class IndicatorEvaluationForm(forms.ModelForm):
    class Meta:
        model = IndicatorEvaluation
        fields = ['score', 'reference_documents', 'explanation']
        widgets = {
            'score': forms.Select(attrs={'style': 'width: 50px;', 'class': 'custom-select'}),
            'reference_documents': forms.Textarea(attrs={'rows': 1, 'id': 'reference-documents'}),
            'explanation': forms.Textarea(attrs={'rows': 1, 'id': 'explanation'}),
        }


IndicatorEvaluationFormSet = forms.modelformset_factory(
    IndicatorEvaluation,
    form=IndicatorEvaluationForm,
    extra=0,  # No additional empty forms
)


class ActionPlanForm(forms.ModelForm):
    class Meta:
        model = ActionPlan
        fields = ['standard', 'objective']
        widgets = {
            'standard': forms.Textarea(attrs={'rows': 1, 'class': 'autosize'}),
            'objective': forms.Textarea(attrs={'rows': 1, 'class': 'autosize'}),
        }

# Form for ActionPlanSteps
class ActionPlanStepsForm(forms.ModelForm):
    class Meta:
        model = ActionPlanSteps
        fields = ['person_responsible', 'action_steps', 'start_date', 'completion_date', 'resources']
        widgets = {
            #'number': forms.Textarea(attrs={'cols': 1, 'rows': 1}),
            'person_responsible': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
            'action_steps': forms.Textarea(attrs={'cols': 30, 'rows': 1, 'class': 'autosize'}),
            'start_date': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
            'completion_date': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
            'resources': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
        }

# Inline formset to manage ActionPlanSteps with ActionPlan
ActionPlanStepsFormSet = inlineformset_factory( ActionPlan, ActionPlanSteps, form=ActionPlanStepsForm, extra=10, can_delete=True)
