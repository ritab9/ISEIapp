from .models import *
from datetime import datetime


def get_principals (teacher):
    principals = User.objects.filter(groups__name='principal', teacher__school=teacher.school)  # get the principal(s) of this teacher
    return principals

def get_principals_emails(teacher):
    principals = get_principals(teacher)
    principal_emails = []
    for p in principals:
        principal_emails.append(p.email)
    return principal_emails


# The last issued certificate for a teacher
def newest_certificate(teacher):
    certificates = TCertificate.objects.filter(teacher=teacher)
    newest_cert = certificates.order_by('-issue_date').first()
    return newest_cert

def ceureport_belongs_to_certificate(ceureport, tcertificate):
    if ceureport.school_year.end_date > tcertificate.issue_date:
        #if tcertificate == newest_certificate(tcertificate.teacher):
        if tcertificate.archived == False:
            return True
        else:
            if ceureport.school_year.end_date < tcertificate.renewal_date:
                return True
    else:
        return False

def academic_class_belongs_to_certificate(academic_class, tcertificate):
#newest is true if there is no certificate with a later issue date
    if academic_class.date_completed > tcertificate.issue_date:
        #if tcertificate == newest_certificate(tcertificate.teacher):
        if tcertificate.archived == False:
            return True
        else:
            if academic_class.date_completed < tcertificate.renewal_date:
                return True
    else:
        return False


 # returns all reports submitted since this certificate was issued
def ceureports_for_certificate(tcertificate):
        ceureport_ids = [ceureport.id for ceureport in CEUReport.objects.filter(teacher=tcertificate.teacher) if
                         ceureport_belongs_to_certificate(ceureport, tcertificate)]
        return CEUReport.objects.filter(id__in=ceureport_ids)

# returns all academic classes since this certificate was issued
def academic_classes_for_certificate(tcertificate):
        academic_class_ids = [academic_class.id for academic_class in AcademicClass.objects.filter(teacher=tcertificate.teacher) if
                         academic_class_belongs_to_certificate(academic_class, tcertificate)]
        return AcademicClass.objects.filter(id__in=academic_class_ids)


def get_today():
    return datetime.date.today()


def certified(teacher):
    if TCertificate.objects.filter(teacher=teacher, renewal_date__gte=date.today()):
        return True
    else:
        return False

def expired_certified(teacher):
    if TCertificate.objects.filter(teacher=teacher, archived= False, renewal_date__lte=date.today()):
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

def expired_current_certificate(teacher):
    return TCertificate.objects.filter(teacher=teacher, archived=False, renewal_date__lt=date.today()).first()

def valid_current_certificate(teacher):
    return TCertificate.objects.filter(teacher=teacher, archived=False, renewal_date__gte=date.today()).first()

def application_submitted(teacher):
    return TeacherCertificationApplication.objects.filter(teacher=teacher)

def get_today():
    return date.today()