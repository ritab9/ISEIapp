# apr/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Progress, PriorityDirective, Directive, Recommendation, ActionPlan, APR


# Signal to update the updated_at field in the related APR model when Progress is updated
@receiver(post_save, sender=Progress)
def update_apr_on_progress_update(sender, instance, created, **kwargs):
    # Check if any of the foreign keys are set, and find the related APR
    apr = None
    print("update")

    # Check each related model to find the APR
    if instance.priority_directive:
        apr = instance.priority_directive.apr
    elif instance.directive:
        apr = instance.directive.apr
    elif instance.recommendation:
        apr = instance.recommendation.apr
    elif instance.action_plan:
        apr = instance.action_plan.apr
    # If we found the related APR, update the updated_at field
    if apr:
        apr.updated_at = timezone.now()  # Set the updated_at field to the current timestamp
        apr.save()  # Save the APR instance to persist the updated_at change