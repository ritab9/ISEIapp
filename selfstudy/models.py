from django.db import models
from accreditation.models import Accreditation,Standard, Indicator
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.core.exceptions import ValidationError


from users.models import StateField, Country, School
from reporting.models import StaffStatus, StaffPosition, SchoolYear
from accreditation.models import IndicatorScore

class CurrentlyEditing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=255)  # Identifies which form is being edited
    last_active = models.DateTimeField(auto_now=True)  # Updated when user interacts
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('form_id', 'user')  # Prevents duplicate locks for the same user

    @staticmethod
    def remove_stale_entries():
        """Remove entries older than 60 minutes (stale locks)."""
        threshold = now() - timedelta(minutes=60)
        CurrentlyEditing.objects.filter(last_active__lt=threshold).delete()

#Models for information needed from the schools (Standards + Inidcators are in Accreditation app)

#Financial Data Keys
class FinancialAdditionalDataKey(models.Model):
    name = models.CharField(max_length=100)
    order_number = models.PositiveIntegerField(default=0, verbose_name="Order Number")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        ordering = ['order_number']
    def __str__(self):
        return self.name

class FinancialTwoYearDataKey(models.Model):
    name = models.CharField(max_length=100)
    order_number = models.PositiveIntegerField(default=0, verbose_name="Order Number")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        ordering = ['order_number']
    def __str__(self):
        return self.name

#Personnel Data Keys
class FTEAssignmentKey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order_number = models.PositiveSmallIntegerField(default=0, verbose_name="Order Number")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order_number']
    def __str__(self):
        return self.name


#Narrative Text (to be used after each Standard)
class StandardNarrative(models.Model):
    text1 = models.TextField(null=True, blank=True)
    text2 = models.TextField(null=True, blank=True)


class ActionPlanInstructionSection(models.Model):
    content = models.TextField()
    number = models.PositiveIntegerField(default=0, verbose_name="Order Number")

    def __str__(self):
        truncated_content = (self.content[:50] + '...') if len(self.content) > 50 else self.content
        return f"Section #{self.number} - {truncated_content}"

class ActionPlanInstructions(models.Model):
    link_text = models.TextField(null=True, blank=True)

    # Relationships
    paragraphs = models.ManyToManyField(ActionPlanInstructionSection, related_name="paragraphs", blank=True)
    procedure_title = models.TextField(null=True, blank=True)
    procedure_title_1 = models.TextField(null=True, blank=True)
    procedure_title_2 = models.TextField(null=True, blank=True)
    procedure_group_1 = models.ManyToManyField(ActionPlanInstructionSection, related_name="procedure_group_1", blank=True)
    procedure_group_2 = models.ManyToManyField(ActionPlanInstructionSection, related_name="procedure_group_2", blank=True)

    def __str__(self):
        return "Action Plan Instructions for SelfStudy"


#Building a SelfStudy for a School
class SelfStudy(models.Model):
    accreditation = models.OneToOneField(Accreditation, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    # status = models.CharField(max_length=20,
    #                          choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed')])

    def __str__(self):
        return f"SelfStudy: {self.accreditation.school},{self.accreditation.visit_date_range()}"

class SelfStudy_Team(models.Model):
    """A team either for coordinating or evaluating a standard."""
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE, related_name="teams")
    standard = models.ForeignKey(Standard, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)

    """Override save to set team name dynamically."""
    def save(self, *args, **kwargs):
        if not self.name:
            if self.standard:
                self.name = f"Standard {self.standard.number} ({self.standard.name}) Team"
            else:
                self.name = "General Coordinating Team"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.standard or 'Coordinating'} Team for {self.selfstudy}"
    class Meta:
        unique_together = ('selfstudy', 'name')

class SelfStudy_TeamMember(models.Model):
    """A member of any team."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(SelfStudy_Team, on_delete=models.CASCADE, related_name="ss_team")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"

#School profile Models

class SchoolProfile(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE)
#A. General Information
    school_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(verbose_name="address", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="city", max_length=64, null=True, blank=True)
    state_us = StateField(verbose_name="US State", blank=True, null=True)
    zip_code = models.CharField(verbose_name="zip/postal code", max_length=8, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    principal = models.CharField(max_length=255, null=True, blank=True)
    board_chair = models.CharField(max_length=255, null=True, blank=True)
    last_evaluation = models.CharField(max_length=255, null=True, blank=True)
    last_interim = models.CharField(max_length=255, null=True, blank=True)

#B. School History
    school_history = models.TextField(null=True, blank=True)

    #this belongs to D
    fte_student_ratio = models.CharField(max_length=10, null=True, blank=True)

#C.Financial Data
class FinancialTwoYearDataEntry(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="two_year_financial_data")
    data_key = models.ForeignKey(FinancialTwoYearDataKey, on_delete=models.CASCADE)
    two_years_ago = models.DecimalField(max_digits =10, decimal_places=2, null=True, blank=True, verbose_name="2 Years Ago")
    one_year_ago = models.DecimalField(max_digits =10, decimal_places=2, null=True, blank=True, verbose_name="1 Year Ago")
    current_year = models.DecimalField(max_digits =10, decimal_places=2, null=True, blank=True, verbose_name="Year to date")
    def __str__(self):
        return f"{self.data_key.name}: {self.two_years_ago}, {self.one_year_ago}"

class FinancialAdditionalDataEntry(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="additional_financial_data")
    data_key = models.ForeignKey(FinancialAdditionalDataKey, on_delete=models.CASCADE)
    value = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return f"{self.data_key.name}: {self.value}"


#D. Personnel Data
class SelfStudyPersonnelData(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="personnel_data")
    first_name=models.CharField(max_length=255, null=True, blank=True)
    last_name=models.CharField(max_length=255, null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    status = models.CharField("status", max_length=2,
                              choices=StaffStatus.choices, default=StaffStatus.FULL_TIME, )
    position = models.ManyToManyField(StaffPosition, blank=True, verbose_name="Assignment/Responsibility")
    highest_degree = models.CharField(max_length=60, null=True, blank=True)
    certification=models.CharField(max_length=255, null=True, blank=True)
    cert_renewal_date=models.DateField(null=True, blank=True)
    endorsements=models.CharField(max_length=400, null=True, blank=True)
    years_experience=models.PositiveSmallIntegerField(null=True, blank=True)
    years_at_this_school=models.PositiveSmallIntegerField(null=True, blank=True)

class ProfessionalActivity(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="activities")
    activity = models.CharField(max_length=255)
    improvement = models.TextField(null=True, blank=True)

class FullTimeEquivalency(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="fte_assignments")
    assignment = models.ForeignKey(FTEAssignmentKey, on_delete=models.CASCADE)
    fte_men = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fte_women = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def total_fte(self):
        return self.fte_men + self.fte_women

    def __str__(self):
        return f"{self.assignment.name} - Men: {self.fte_men}, Women: {self.fte_women}"


#E. Student Data
class StudentEnrollmentData(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="enrollment_data")
    projected_enrollment_next_year = models.PositiveSmallIntegerField(null=True, blank=True)
    projected_enrollment_2_years = models.PositiveSmallIntegerField(null=True, blank=True)
    projected_enrollment_3_years = models.PositiveSmallIntegerField(null=True, blank=True)

class StudentFollowUpDataKey(models.Model):
    LEVEL_CHOICES = [
        ('elementary', 'Elementary'),
        ('secondary', 'Secondary'),
    ]

    description = models.CharField(max_length=255, null=True, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    order_number = models.PositiveIntegerField(default=0, verbose_name="Order Number")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        ordering = ['level', 'order_number']

    def __str__(self):
        return f"{self.description} ({self.get_level_display()})"


class StudentFollowUpDataEntry(models.Model):
    school=models.ForeignKey(School, on_delete=models.CASCADE, related_name="followup_entries")
    school_year=models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="followup_entries")
    followup_data_key = models.ForeignKey(StudentFollowUpDataKey, on_delete=models.CASCADE)
    value = models.SmallIntegerField(null=True, blank=True)

class StudentAchievementData(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="achievement_data")
    communication_parents = models.TextField(null=True, blank=True)
    process_to_improve = models.TextField(null=True, blank=True)

class GradeLevelTest(models.Model):
    achievement_data = models.ForeignKey(StudentAchievementData, on_delete=models.CASCADE, related_name="grade_level_tests")
    grade_level = models.CharField(max_length=50)
    test_administered = models.TextField()

    def __str__(self):
        return f"{self.grade_level}: {self.test_administered}"


class StandardizedTestSession(models.Model):
    TEST_TYPE_CHOICES = [
        ('IOWA', 'IOWA'),
        ('ACT', 'ACT'),
        ('SAT', 'SAT'),
        ('OT', 'OTHER')
    ]

    ACT_NAMES = ['ACT', 'PreACT', 'PreACT8_9', 'Aspire']
    SAT_NAMES = ['SAT', 'PSAT', 'PSAT10', 'PSAT8_9']

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='test_sessions')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='test_sessions')
    test_type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=100, null=True, blank=True)  # Validate based on test_type in clean()
    grade_level_type = models.CharField(max_length=10, choices=[('elementary', 'Elementary'), ('secondary', 'Secondary')], default ='secondary')
    class Meta:
        unique_together = ('school', 'school_year', 'test_type', 'test_name', 'grade_level_type')

    def __str__(self):
        return f"{self.school.name}: {self.school_year.name} - {self.test_type}"

class StandardizedTestScore(models.Model):
    SUBJECT_CHOICES = [
        ('ENGLISH', 'English'),
        ('READING', 'Reading'),
        ('WRITING', 'Writing'),
        ('MATH', 'Mathematics'),
        ('SCIENCE', 'Science'),
        ('SOCIAL STUDIES', 'Social Studies'),
        ('COMPOSITE', 'Composite Score'),
    ]

    session = models.ForeignKey(StandardizedTestSession, on_delete=models.CASCADE, related_name='scores')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    grade = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)], null=True, blank=True)  # Validated to be 1–8 or 9–12 based on session
    score = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('session', 'subject', 'grade')

    def clean(self):
        if self.session.grade_level_type == 'elementary' and not (1 <= self.grade <= 8):
            raise ValidationError("Elementary tests must be for grades 1 through 8.")
        if self.session.grade_level_type == 'secondary' and not (9 <= self.grade <= 12):
            raise ValidationError("Secondary tests must be for grades 9 through 12.")


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SecondaryCurriculumCourse(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="secondary_curriculum")
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name="courses")
    course_title = models.CharField(max_length=200)
    teacher_name = models.CharField(max_length=200)
    certification_endorsed = models.BooleanField(default=False)
    credit_value = models.DecimalField(max_digits=4, decimal_places=2)
    periods_per_week = models.PositiveIntegerField()
    minutes_per_week = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course_title} ({self.teacher_name})"

class OtherCurriculumData(models.Model):
    school_profile = models.OneToOneField(SchoolProfile, on_delete=models.CASCADE, related_name="other_curriculum_data")
    dual_enrollment_number=models.SmallIntegerField(blank=True, null=True)
    dual_enrollment_location=models.CharField(max_length=2225, blank=True, null=True)
    dual_enrollment_courses = models.CharField(max_length=2225, blank=True, null=True)
    vocational_certificate_areas = models.CharField(max_length=2225, blank=True, null=True)

class SupportService(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="support_services")
    academic_advisement=models.TextField(null=True, blank=True)
    career_advisement=models.TextField(null=True, blank=True)
    personal_counseling=models.TextField(null=True, blank=True)

class PhilantrophyProgram(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="philantrophy_program")
    development_program=models.TextField(null=True, blank=True)

#Standard Scoring Model
class StandardEvaluation(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE, related_name='standard_evaluations')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    narrative =models.TextField(null=True, blank=True)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"Evaluation for {self.standard} (Score: {self.average_score})"


#Indicator Scoring Models
class IndicatorEvaluation(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE, related_name='indicator_evaluations')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)  # Add this field
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evaluations')

    indicator_score = models.ForeignKey(IndicatorScore, on_delete=models.CASCADE, null=True, blank=True)

    SCORE_CHOICES = (
        (4, 4),
        (3, 3),
        (2, 2),
        (1, 1),
    )
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, null=True, blank=True)
    reference_documents = models.TextField(null=True, blank=True)  # Store references as a comma-separated list or JSON
    explanation = models.TextField(null=True, blank=True)
    class Meta:
        unique_together = [['selfstudy', 'indicator']]  # Ensure no duplicate evaluations for the same indicator
        indexes = [
            models.Index(fields=['selfstudy', 'standard']),
            models.Index(fields=['selfstudy', 'indicator']),
        ]
        ordering = ['selfstudy', 'standard', 'indicator']

    def __str__(self):
        score_display = self.get_score_display() or 'Not Scored'
        return f"Evaluation for {self.indicator} (Score: {score_display})"


class MissionAndObjectives(models.Model):
    selfstudy=models.ForeignKey(SelfStudy, on_delete=models.CASCADE, related_name='objectives')
    mission_statement = models.TextField(null=True, blank=True)
    vision_statement = models.TextField(null=True, blank=True)
    philosophy_statement = models.TextField(null=True, blank=True)
    school_objectives = models.TextField(help_text="", null=True, blank=True)

    def __str__(self):
        return f"Mission, Objectives of {self.selfstudy.accreditation.school.name}"  # Adjust as needed
