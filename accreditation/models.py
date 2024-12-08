from django.db import models
from users.models import School
from django.db.models import Q


class AccreditationTerm(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=60)
    description = models.TextField()
    def __str__(self):
        return self.code + " " + self.name

class Accreditation(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    visit_start_date = models.DateField(null=True, blank=True)
    visit_end_date = models.DateField(null=True, blank=True)
    term = models.ForeignKey(AccreditationTerm, on_delete=models.CASCADE)
    term_start_date = models.DateField(null=True, blank=True)
    term_end_date = models.DateField(null=True, blank=True)
    current_accreditation = models.BooleanField(default=False)

    def __str__(self):
        return f"Accreditation: School {self.school}, {self.term_start_date.strftime('%Y')} - {self.term_end_date.strftime('%Y')}"

    def save(self, *args, **kwargs):
        # check if there is a previous currently active accreditation for the school
        previous_accreditations = Accreditation.objects.filter(Q(school=self.school) & Q(current_accreditation=True))

        if self.pk is None:  # object is being created, not updated
            # if there are active accreditations mark them as inactive before saving this one as current
            for accreditation in previous_accreditations:
                accreditation.current_accreditation = False
                accreditation.save()
        elif self.current_accreditation:
            # updating the object, there should not be any other active accreditation apart from current
            previous_accreditations.exclude(pk=self.pk).update(current_accreditation=False)

        super().save(*args, **kwargs)  # Call the "real" save() method