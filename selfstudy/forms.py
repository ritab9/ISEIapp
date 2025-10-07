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
        initial_users = team.ss_team.values_list('user', flat=True)
        self.initial['users'] = User.objects.filter(id__in=initial_users)

    def save(self, team):
        """Save the selected users to the team."""
        selected_users = self.cleaned_data['users']
        current_members = team.ss_team.all()

        # Add new users
        for user in selected_users:
            if not SelfStudy_TeamMember.objects.filter(team=team, user=user).exists():
                SelfStudy_TeamMember.objects.create(user=user, team=team)
                user.groups.add(Group.objects.get(name="coordinating_team"))

        # Remove unchecked users
        for member in current_members:
            if member.user not in selected_users:
                member.delete()


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = [
            "school_name", "address", "city", "state_us", "zip_code",
            "country", "principal", "board_chair", "last_evaluation", "last_interim"
        ]
        widgets = {
            'address': forms.TextInput(attrs={'style': 'width: 250px;'}),
            'last_evaluation': forms.TextInput(attrs={'style': 'width: 250px;'}),
        }


class SchoolHistoryForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['school_history']  # Add fields you want to display in the form

class FinancialTwoYearDataEntryForm(forms.ModelForm):
    class Meta:
        model = FinancialTwoYearDataEntry
        fields = ['id','two_years_ago', 'one_year_ago', 'current_year']
        labels = {'two_years_ago': 'Two Years Ago','one_year_ago': 'One Year Ago', 'current_year': 'Year to Date'}

    two_years_ago = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )
    one_year_ago = forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )
    current_year = forms.DecimalField(
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

class FullTimeEquivalencyForm(forms.ModelForm):
    class Meta:
        model = FullTimeEquivalency
        fields = ['id', 'fte_men','fte_women']

    fte_men=forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )
    fte_women=forms.DecimalField(
        required=False, max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'style': 'text-align: right; width: 120px;'})
    )

FTEFormSet = modelformset_factory(FullTimeEquivalency, form=FullTimeEquivalencyForm, extra=0, can_delete=False)

class FTEEquivalencyForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = ['fte_student_ratio']

class StandardEvaluationForm(forms.ModelForm):
    class Meta:
        model = StandardEvaluation
        fields = ['narrative', 'average_score']  # Include only narrative and average_score fields

        widgets = {
            'narrative': forms.Textarea(attrs={'rows': 2}),
            'average_score': forms.HiddenInput(),
        }

class IndicatorScoreSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

        try:
            # If value is a model instance or a PK, get the associated IndicatorScore
            score = IndicatorScore.objects.get(pk=value)
            option['attrs']['data-level'] = score.level
            option['attrs']['data-comment'] = score.comment
        except Exception:
            pass  # In case it's a blank or invalid

        return option


class IndicatorEvaluationForm(forms.ModelForm):
    class Meta:
        model = IndicatorEvaluation
        fields = ['indicator_score', 'reference_documents', 'explanation']
        widgets = {
            'indicator_score': IndicatorScoreSelect(attrs={
                'class': 'indicator-score-dropdown',
            }),
            'reference_documents': forms.Textarea(attrs={'rows': 1, 'id': 'reference-documents'}),
            'explanation': forms.Textarea(attrs={'rows': 3, 'id': 'explanation'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # THIS LINE IS CRITICAL

        self.fields['indicator_score'].choices = [('', '--- Select ---')] + [
            (score.pk, f"{score.get_score_display()} ")
            for score in IndicatorScore.objects.all()
        ]

IndicatorEvaluationFormSet = forms.modelformset_factory(IndicatorEvaluation, form=IndicatorEvaluationForm, extra=0)


class MissionAndObjectivesForm(forms.ModelForm):
    class Meta:
        model = MissionAndObjectives
        fields = ['mission_statement', 'vision_statement', 'philosophy_statement', 'school_objectives']
        widgets = {
            'mission_statement': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
            'vision_statement': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
            'philosophy_statement': forms.Textarea(attrs={'rows': 10, 'cols': 60}),
            'school_objectives': forms.Textarea(attrs={'rows': 10, 'cols': 60}),
        }

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


class ProfessionalActivityForm(forms.ModelForm):
    class Meta:
        model = ProfessionalActivity
        fields = ['activity', 'improvement']
        widgets={
            'activity': forms.Textarea(attrs={'cols': 50, 'rows': 1 }),
            'improvement': forms.Textarea(attrs={'cols': 300, 'rows': 1 }),
        }

ProfessionalActivityFormSet = inlineformset_factory(SchoolProfile, ProfessionalActivity, form=ProfessionalActivityForm, extra=4)


class StudentEnrollmentDataForm(forms.ModelForm):
    class Meta:
        model = StudentEnrollmentData
        fields = [
            'projected_enrollment_next_year',
            'projected_enrollment_2_years',
            'projected_enrollment_3_years',
        ]
        widgets = {
            'projected_enrollment_next_year': forms.NumberInput(attrs={'style': 'width: 80px;',}),
            'projected_enrollment_2_years': forms.NumberInput(attrs={'style': 'width: 80px;',}),
            'projected_enrollment_3_years': forms.NumberInput(attrs={'style': 'width: 80px;',}),
        }


class StudentAchievementDataForm(forms.ModelForm):
    class Meta:
        model = StudentAchievementData
        fields = ['communication_parents', 'process_to_improve']
        widgets = {
            'communication_parents': forms.Textarea(attrs={'class': '', 'rows': 2}),
            'process_to_improve': forms.Textarea(attrs={'class': '', 'rows': 2}),
        }

class GradeLevelTestForm(forms.ModelForm):
    class Meta:
        model = GradeLevelTest
        fields = ['grade_level', 'test_administered']
        widgets = {
            'grade_level': forms.TextInput(attrs={'class': ''}),
            'test_administered': forms.Textarea(attrs={'class': '', 'rows': 1}),
        }


SUBJECT_CHOICES = StandardizedTestScore.SUBJECT_CHOICES
GRADE_CHOICES = [(i, str(i)) for i in range(1, 13)]

class StandardizedTestSessionForm(forms.ModelForm):
    class Meta:
        model = StandardizedTestSession
        fields = ['test_type', 'test_name']
        widgets = {
            'test_type': forms.Select(attrs={'class': ''}),
            'test_name': forms.Textarea(attrs={'rows': 1, 'cols':70 }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: restrict name options based on test type dynamically
        self.fields['test_name'].widget.attrs.update({'placeholder': 'Optional additional Info: missing Test Type, Test sub-name (Aspire, PreSAT), etc.'})


class StandardizedTestScoreForm(forms.ModelForm):
    class Meta:
        model = StandardizedTestScore
        fields = ['subject', 'grade', 'score']
        widgets = {
            'subject': forms.HiddenInput(),
            'grade': forms.HiddenInput(),
            'score': forms.NumberInput(attrs={'class': 'form-control form-control-sm w-30', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].required = False  # 👈 allow leaving it blank

class SupportServiceForm(forms.ModelForm):
    class Meta:
        model = SupportService
        fields = ['academic_advisement', 'career_advisement', 'personal_counseling']  # Add the fields you want to display
        widgets = {
            'academic_advisement': forms.Textarea(attrs={'rows': '2', }),
            'career_advisement': forms.Textarea(attrs={'rows': '2', }),
            'personal_counseling': forms.Textarea(attrs={'rows': '2', }),
        }

class PhilantrophyProgramForm(forms.ModelForm):
    class Meta:
        model = PhilantrophyProgram
        fields = ['development_program']
        widgets={
            'development_program':forms.Textarea
        }

class SecondaryCurriculumCourseForm(forms.ModelForm):
    teacher_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'list': 'teacher-list'}))
    class Meta:
        model = SecondaryCurriculumCourse
        fields = [
            'course_title',
            'teacher_name',
            'certification_endorsed',
            'credit_value',
            'periods_per_week',
            'minutes_per_week',
        ]

        widgets = {
            'credit_value': forms.NumberInput(attrs={'style': 'width: 70px;'}),
            'periods_per_week': forms.NumberInput(attrs={'style': 'width: 70px;'}),
            'minutes_per_week': forms.NumberInput(attrs={'style': 'width: 90px;'}),
        }


class OtherCurriculumDataForm(forms.ModelForm):
    class Meta:
        model = OtherCurriculumData
        exclude=['school_profile']

        widgets = {
            'dual_enrollment_location': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'e.g., Local community college campus or online via university partnership'
            }),
            'dual_enrollment_courses': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'e.g., College Algebra, Intro to Psychology, Composition I'
            }),
            'vocational_certificate_areas': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'e.g., CNA, Auto Mechanics, Culinary Arts'
            }),
            'dual_enrollment_number': forms.NumberInput(attrs={
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔹 Explicitly make this optional
        self.fields['dual_enrollment_number'].required = False