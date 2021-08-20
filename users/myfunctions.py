from .models import *
from teachercert.models import TCertificate


# teacher application received
def initial_application(teacher):
    applications = TeacherCertificationApplication.objects.filter(teacher=teacher)
    first_application = applications.order_by('date').first()
    return first_application

def last_application(teacher):
    applications = TeacherCertificationApplication.objects.filter(teacher=teacher)
    last_application = applications.order_by('date').last()
    return last_application

def certified(teacher):
    if TCertificate.objects.filter(teacher=teacher):
        return True
    else:
        return False
