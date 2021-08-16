from .models import *

def pdareport_belongs_to_certificate(pdareport, tcertificate):
    #print('function called')
    if pdareport.teacher == tcertificate.teacher:
        if pdareport.school_year.end_date > tcertificate.issue_date:
            #print(str(pdareport.school_year.end_date))
            #print(str(tcertificate.issue_date))
            #print('return True')
            return True
    else:
        #print('return False')
        return False


def academic_class_belongs_to_certificate(academic_class, tcertificate, newest):
#newest is true if there is no certificate with a later issue date
    if academic_class.teacher == tcertificate.teacher:
        if academic_class.date_completed > tcertificate.issue_date:
            if tcertificate == newest:
                return True
            else:
                if academic_class.date_completed < tcertificate.renewal_date:
                    return True
    else:
        return False