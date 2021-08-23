from .models import *
from teachercert.models import TCertificate
from datetime import date



def certified(teacher):
    if TCertificate.objects.filter(teacher=teacher, renewal_date__gte=date.today()):
        return True
    else:
        return False

def never_certified(teacher):
    if TCertificate.objects.filter(teacher=teacher,):
        return False
    else:
        return True

def current_certificates(teacher):
    return TCertificate.objects.filter(teacher=teacher, archived=False)

def get_today():
    return date.today()
