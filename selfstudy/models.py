from django.db import models
from accreditation.models import Accreditation,Standard, Indicator


#Financial Data Keys
class FinancialAdditionalDataKey(models.Model):
    name = models.CharField(max_length=50)
    order_number = models.PositiveIntegerField(default=0, verbose_name="Order Number")
    class Meta:
        ordering = ['order_number']
    def __str__(self):
        return self.name

class FinancialTwoYearDataKey(models.Model):
    name = models.CharField(max_length=50)
    order_number = models.PositiveIntegerField(default=0, verbose_name="Order Number")
    class Meta:
        ordering = ['order_number']
    def __str__(self):
        return self.name


#Building a SelfStudy for a School
class SelfStudy(models.Model):
    accreditation = models.ForeignKey(Accreditation, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    # status = models.CharField(max_length=20,
    #                          choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('reviewed', 'Reviewed')])

    def __str__(self):
        return f"SelfStudy: {self.accreditation.school}"

class CoordinatingTeam(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE)
    coordinating_team = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return f"CoordinatingTeam: {self.coordinating_team}"

class TeamMember(models.Model):
    coordinating_team = models.ForeignKey(CoordinatingTeam, on_delete=models.CASCADE, related_name='team_members')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    members = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"TeamMember for {self.standard}: {self.members}"

class SchoolProfile(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE)
    school_history = models.TextField(null=True, blank=True)
    #delete JSONFields if will adopt database Entries
    financial_2year_data = models.JSONField(null=True, blank=True)
    financial_additional_data = models.JSONField(null=True, blank=True)
#TODO Finalize school Profile


class IndicatorEvaluation(models.Model):
    selfstudy = models.ForeignKey(SelfStudy, on_delete=models.CASCADE, related_name='indicator_evaluations')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)  # Add this field
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='evaluations')
    SCORE_CHOICES = (
        (1, 'Not Met'),
        (2, 'Partially Met'),
        (3, 'Met'),
        (4, 'Exceptional'),
    )
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, null=True, blank=True)
    reference_documents = models.TextField(null=True, blank=True)  # Store references as a comma-separated list or JSON
    explanation = models.TextField(null=True, blank=True)
    class Meta:
        unique_together = [['selfstudy', 'indicator']]  # Ensure no duplicate evaluations for the same indicator

    def __str__(self):
        score_display = self.get_score_display() or 'Not Scored'
        return f"Evaluation for {self.indicator} (Score: {score_display}, SelfStudy: {self.selfstudy})"


#Delete Database Entries if choosing JSON fields
class FinancialTwoYearDataEntries(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE)
    financial_data_category = models.ForeignKey(FinancialTwoYearDataKey, on_delete=models.CASCADE)
    two_years_ago = models.DecimalField(max_digits =10, decimal_places=2, null=True, blank=True, verbose_name="2 Years Ago")
    one_year_ago = models.DecimalField(max_digits =10, decimal_places=2, null=True, blank=True, verbose_name="1 Year Ago")
class FinancialAdditionalDataEntries(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name="other_financial_data")
    other_financial_data = models.ForeignKey(FinancialAdditionalDataKey, on_delete=models.CASCADE)
    response = models.CharField(max_length=50, null=True, blank=True)