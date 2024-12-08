#forms.py

from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from .models import PriorityDirective, Directive, Recommendation, ActionPlan, ActionPlanSteps


#base form to be used for PriorityDirective, Directive and Recommendation Forms
class BaseDirectiveForm(forms.ModelForm):
    class Meta:
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 2,
                'cols': 40,
                #'style': 'resize: none;',
            }),
        }
class PriorityDirectiveForm(BaseDirectiveForm):
    class Meta(BaseDirectiveForm.Meta):
        model = PriorityDirective
class DirectiveForm(BaseDirectiveForm):
    class Meta(BaseDirectiveForm.Meta):
        model = Directive
class RecommendationForm(BaseDirectiveForm):
    class Meta(BaseDirectiveForm.Meta):
        model = Recommendation


# Formsets using the customized forms
PriorityDirectiveFormSet = modelformset_factory( PriorityDirective, form=PriorityDirectiveForm, extra=10, can_delete=True)
DirectiveFormSet = modelformset_factory(Directive, form=DirectiveForm, extra=10, can_delete=True)
RecommendationFormSet = modelformset_factory( Recommendation, form=RecommendationForm, extra=10, can_delete=True)

# Form for ActionPlan
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
        fields = ['person_responsible', 'action_steps', 'timeline', 'resources']
        widgets = {
            #'number': forms.Textarea(attrs={'cols': 1, 'rows': 1}),
            'person_responsible': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
            'action_steps': forms.Textarea(attrs={'cols': 30, 'rows': 1, 'class': 'autosize'}),
            'timeline': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
            'resources': forms.Textarea(attrs={'cols': 5, 'rows': 1, 'class': 'autosize'}),
        }

# Inline formset to manage ActionPlanSteps with ActionPlan
ActionPlanStepsFormSet = inlineformset_factory( ActionPlan, ActionPlanSteps, form=ActionPlanStepsForm, extra=10, can_delete=True)
