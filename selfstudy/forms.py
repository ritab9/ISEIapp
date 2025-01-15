from django import forms
from .models import SchoolProfile, IndicatorEvaluation

class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['school_history', 'financial_2year_data', 'financial_additional_data']  # Adjust as needed

class IndicatorEvaluationForm(forms.ModelForm):
    class Meta:
        model = IndicatorEvaluation
        fields = ['score', 'reference_documents', 'explanation']

IndicatorEvaluationFormSet = forms.modelformset_factory(
    IndicatorEvaluation,
    form=IndicatorEvaluationForm,
    extra=0,  # No additional empty forms
)
