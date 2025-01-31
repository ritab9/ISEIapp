from django import forms
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from django.db.models import Q

from .models import *
from apr.models import ActionPlan, ActionPlanSteps
from django.contrib.auth.models import Group
from reporting.models import Personnel, StaffStatus

class SelfStudy_TeamMemberForm(forms.Form):
    """Form to add or remove team members for a given team."""
    users = forms.ModelMultipleChoiceField( queryset=User.objects.none(), widget=forms.CheckboxSelectMultiple, required=False)
    def __init__(self, *args, **kwargs):
        selfstudy = kwargs.pop('selfstudy')
        team = kwargs.pop('team')
        super().__init__(*args, **kwargs)

        # Show all active users from the school (personnel that has accounts on ISEIapp)
        school = selfstudy.accreditation.school
        self.fields['users'].queryset = school.get_active_users()

        # Pre-check users who are already part of the given team
        initial_users = team.selfstudy_teammember_set.values_list('user', flat=True)
        self.initial['users'] = User.objects.filter(id__in=initial_users)

    def save(self, team):
        """Save the selected users to the team."""
        selected_users = self.cleaned_data['users']
        current_members = team.selfstudy_teammember_set.all()

        # Add new users
        for user in selected_users:
            if not SelfStudy_TeamMember.objects.filter(team=team, user=user).exists():
                SelfStudy_TeamMember.objects.create(user=user, team=team)
                user.groups.add(Group.objects.get(name="coordinating_team"))

        # Remove unchecked users
        for member in current_members:
            if member.user not in selected_users:
                member.delete()


class SchoolHistoryForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['school_history']  # Add fields you want to display in the form

class FinancialTwoYearDataEntryForm(forms.ModelForm):
    class Meta:
        model = FinancialTwoYearDataEntry
        fields = ['id','two_years_ago', 'one_year_ago']
        labels = {'two_years_ago': 'Two Years Ago','one_year_ago': 'One Year Ago',}

    two_years_ago = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )
    one_year_ago = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )

class FinancialAdditionalDataEntryForm(forms.ModelForm):
    class Meta:
        model = FinancialAdditionalDataEntry
        fields = ['id','value']
        labels = { 'value': 'Value'}

    value = forms.CharField(required=False)

FinancialTwoYearDataFormSet = modelformset_factory(FinancialTwoYearDataEntry, form=FinancialTwoYearDataEntryForm, extra=0, can_delete=False)
FinancialAdditionalDataFormSet = modelformset_factory(FinancialAdditionalDataEntry,form=FinancialAdditionalDataEntryForm, extra=0, can_delete=False)

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
            'score': forms.Select(attrs={'style': 'width: 45px; font-size: 14px;', 'class': 'custom-select'}),
            'reference_documents': forms.Textarea(attrs={'rows': 1, 'id': 'reference-documents'}),
            'explanation': forms.Textarea(attrs={'rows': 1, 'id': 'explanation'}),
        }


IndicatorEvaluationFormSet = forms.modelformset_factory(IndicatorEvaluation, form=IndicatorEvaluationForm, extra=0)


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
            'person_responsible': forms.Textarea(attrs={'cols': 10, 'rows': 3 }),
            'action_steps': forms.Textarea(attrs={'cols': 50, 'rows': 3 }),
            'start_date': forms.Textarea(attrs={'cols': 10, 'rows': 3 }),
            'completion_date': forms.Textarea(attrs={'cols': 10, 'rows': 3 }),
            'resources': forms.Textarea(attrs={'cols': 10, 'rows': 3 }),
        }

# Inline formset to manage ActionPlanSteps with ActionPlan
ActionPlanStepsFormSet = inlineformset_factory( ActionPlan, ActionPlanSteps, form=ActionPlanStepsForm, extra=10, can_delete=True)
