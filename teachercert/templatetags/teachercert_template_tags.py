from django import template
from teachercert.myfunctions import *

register = template.Library()

@register.filter
def certified(teacher):
    return certified(teacher)


@register.filter
def applied(teacher):
    return applied(teacher)

# TODO review this and delete or finalize
#not used but theoretically could be used to filter on the template
# https://docs.djangoproject.com/en/1.11/howto/custom-template-tags/

#@register.filter
#def ceu_reports_certificate(tcertificate):
#    return ceureports_for_certificate(tcertificate)

#@register.filter
#def ceu_reports_certificate(tcertificate):
#    return academic_classes_for_certificate(tcertificate)