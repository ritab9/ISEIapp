from .models import *

def pdareport_belongs_to_certificate(pdareport, tcertificate):
    #print('function called')
    if pdareport.school_year.end_date > tcertificate.issue_date:
        #print(str(pdareport.school_year.end_date))
        #print(str(tcertificate.issue_date))
        #print('return True')
        return True
    else:
        #print('return False')
        return False
