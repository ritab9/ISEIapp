from django.db import models
from accreditation.models import Accreditation
from users.models import School


# Create your models here.
class APR(models.Model):
    accreditation = models.OneToOneField(Accreditation, on_delete=models.CASCADE)

    def __str__(self):
        return f"APR: {self.accreditation.school}, {self.accreditation.term_start_date.strftime('%Y')} - {self.accreditation.term_end_date.strftime('%Y')}"


class APRSchoolYear(models.Model):
    name=models.CharField(max_length=10, unique=True)
    apr = models.ForeignKey(APR, on_delete=models.CASCADE, related_name='aprschoolyear', null=True, blank=True)

    def __str__(self):
        return self.name

class ProgressStatus(models.Model):
    status = models.CharField(max_length=20)
    def __str__(self):
        return self.status

class PriorityDirective(models.Model):
    number = models.IntegerField()
    apr = models.ForeignKey(APR, on_delete=models.CASCADE)
    progress_status = models.ForeignKey(ProgressStatus, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.number:
            # Get the highest number for the current APR and add 1
            max_number = PriorityDirective.objects.filter(apr=self.apr).aggregate(models.Max('number'))['number__max']
            self.number = (max_number or 0) + 1
        super(PriorityDirective, self).save(*args, **kwargs)

    def __str__(self):
        return f"Priority Directive {self.number}"

class Directive(models.Model):
    number = models.IntegerField()
    apr = models.ForeignKey(APR, on_delete=models.CASCADE)
    progress_status = models.ForeignKey(ProgressStatus, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.number:
            # Get the highest number for the current APR and add 1
            max_number = Directive.objects.filter(apr=self.apr).aggregate(models.Max('number'))['number__max']
            self.number = (max_number or 0) + 1
        super(Directive, self).save(*args, **kwargs)

    def __str__(self):
        return f"Directive {self.number}"

class Recommendation(models.Model):
    number = models.IntegerField()
    apr = models.ForeignKey(APR, on_delete=models.CASCADE)
    progress_status = models.ForeignKey(ProgressStatus, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.number:
            # Get the highest number for the current APR and add 1
            max_number = Recommendation.objects.filter(apr=self.apr).aggregate(models.Max('number'))['number__max']
            self.number = (max_number or 0) + 1
        super(Recommendation, self).save(*args, **kwargs)

    def __str__(self):
        return f"Recommendation {self.number}"


class ActionPlan(models.Model):
    number = models.IntegerField()
    apr = models.ForeignKey(APR, on_delete=models.CASCADE)
    standard = models.TextField()
    objective = models.TextField()
    progress_status = models.ForeignKey(ProgressStatus, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the number for new instances
            existing_count = ActionPlan.objects.filter(apr=self.apr).count()
            self.number = existing_count + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Action Plan #{self.number}"

class ActionPlanSteps(models.Model):
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE)
    number = models.IntegerField(null=True, blank=True)
    person_responsible = models.TextField(verbose_name="Person(s) Responsible")
    action_steps = models.TextField(verbose_name="Action Steps")
    timeline = models.TextField(verbose_name="Date/Timeline")
    resources = models.TextField(verbose_name="Estimated Resources")

    def __str__(self):
        return f"Action Plan #{self.number}"

class Progress(models.Model):
    school_year = models.ForeignKey(APRSchoolYear, on_delete=models.CASCADE, related_name="progress")
    description = models.TextField(default="")

    # Connect Progress to Specific Entities
    priority_directive = models.ForeignKey(PriorityDirective, on_delete=models.CASCADE, null=True, blank=True,
                                           related_name="progress")
    directive = models.ForeignKey(Directive, on_delete=models.CASCADE, null=True, blank=True, related_name="progress")
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name="progress")
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="progress")

    def __str__(self):
        if self.priority_directive:
            return f"Progress {self.priority_directive}, {self.school_year}"
        elif self.directive:
            return f"Progress {self.directive}, {self.school_year}"
        elif self.recommendation:
            return f"Progress {self.recommendation}, {self.school_year}"
        elif self.action_plan:
            return f"Progress {self.action_plan}, {self.school_year}"
        else:
            return f"Progress {self.school_year}"