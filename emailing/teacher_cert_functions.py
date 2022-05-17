
from django.core.mail import EmailMessage
from django.conf import settings


#from teachercert.models import EmailMessageTemplate

# TODO embed office_email and signature as an env variable (or think of some other way to do it)
signature = "\n" + "\n" +"Rita Burjan" + "\n" + "ISEI Teacher Certification" + "\n" + "isei1.org"
office_email = ["jodyv@isei.life"]
#office_email = ["oldagape@yahoo.com"]


def send_email(subject, message, send_to = ["teacher_certification@iseiea.org"]):
    message = message+signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, send_to, cc=["teacher_certification@iseiea.org"])
    mail.send()

def email_registered_user(teacher):
    subject = "ISEI Teacher Certification Account"
    message = "Dear "+  str(teacher.first_name) + ", " + "\n" + "\n" + \
               "An account has been created for you to apply for and manage your ISEI teacher certification." + \
              "\n" + "\n " + "Your username is: " + str(teacher.first_name) + "." + str(teacher.last_name) + \
              "\n" + "Follow this link to create a password for your account: https://isei1.org/reset_password/ "+ \
              "\n" + "\n " + "After login you can access the Teacher Certification Handbook (bottom right corner of the website). Sections 5-7 offer guidance for using the website." +\
              "\n" + "\n " + "If you have any questions, please contact us."
    # str(EmailMessageTemplate.objects.get(name="RegisterUser").message) + \
    send_email(subject, message, [teacher.user.email])

def email_AcademicClass_submitted(teacher):
    subject = "Academic Class: " + str(teacher)
    message = str(teacher) + " from " +str(teacher.school.name) + " has submitted an academic class. \n \nisei1.org "
    send_email(subject, message)
    #message = message + signature
    #mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, cc =["teacher_certification@iseiea.org"])
    #mail.send()

def email_CEUReport_created(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = str(teacher) + " from " +str(teacher.school.name) + " has initiated a CEU Report for the " + school_year_name + " school year. isei1.org"
    send_email(subject, message)

def email_CEUReport_submitted(teacher, principal_emails, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = str(teacher) + " from " +str(teacher.school.name) + " has submitted a CEU Report for the " + school_year_name + " school year." + "\n " + "Log in to isei1.org in order to review and approve the CEU Report. ISEI will NOT receive the report unless you review it. "
    send_email(subject, message, principal_emails)

#two_emails
def email_CEUReport_approved_by_principal(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message1 = str(teacher) + "'s, from " +str(teacher.school.name) + ",  " + school_year_name + " CEU Report was reviewed by the principal." + "\n " + " Log in to isei1.org in order to review and approve the CEU Report. "
    message1 = message1 + signature
    mail1 = EmailMessage(subject, message1, settings.EMAIL_HOST_USER, ["teacher_certification@iseiea.org"])
    mail1.send()
    #  mail1 = (subject, message1, settings.EMAIL_HOST_USER, ["teacher_certification@iseiea.org"])
    message2 = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was reviewed by the principal and submitted to ISEI. It will be reviewed by ISEI shortly."
    message2 = message2 + signature
    #mail2 = (subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email],["teacher_certification@iseiea.org"])
    mail2 = EmailMessage(subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email],["teacher_certification@iseiea.org"])
    mail2.send()
    #send_mass_mail((mail1, mail2), fail_silently= False)

def email_CEUReport_denied_by_principal(teacher,school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was considered incomplete by the principal. Please log in to isei1.org ,review, update and resubmit your Report. Contact your principal if further clarifications are needed."
    send_email(subject,message,[teacher.user.email])

def email_CEUReport_retracted_by_principal(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) + "," + "\n " + "The principal has canceled the previous action on your CEU Report. If a new action is not taken soon, please contact your principal."
    send_email(subject,message,[teacher.user.email])

#two_email
def email_CEUactivity_approved_by_principal(teacher):
    subject = "CEU Activity: " + str(teacher)
    message1 = str(teacher) + "'s, from " +str(teacher.school.name) + ", CEU activity was reviewed by the principal. Log in to isei1.org in order to review and approve the CEU Activity. "
    message1 = message1 + signature
    mail1 =EmailMessage(subject, message1, settings.EMAIL_HOST_USER, ["teacher_certification@iseiea.org"])
    message2 = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was reviewed by the principal and submitted to ISEI. It will be reviewed shortly."
    message2 = message2 + signature
    mail2 = EmailMessage(subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email], ["teacher_certification@iseiea.org"])
    mail1.send()
    mail2.send()
    #send_mass_mail((mail1, mail2), fail_silently= False)


def email_CEUactivity_denied_by_principal(teacher):
    subject = "CEU Report: " + str(teacher)
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was considered incomplete by the principal. Please log in to isei1.org ,review, update and resubmit your CEU Activity."
    send_email(subject,message,[teacher.user.email])


def email_CEUReport_approved_by_ISEI(teacher,school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was reviewed by ISEI. Please sign in to isei1.org to review the approved activities and CEUs."
    send_email(subject,message,[teacher.user.email])

def email_CEUReport_denied_by_ISEI(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was considered incomplete by ISEI. Please log in to isei1.org ,review, update and resubmit your Report."
    send_email(subject,message,[teacher.user.email])

def email_CEUReport_retracted_by_ISEI(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) + "," + "\n " + "ISEI has canceled the previous action on your CEU Report. A new action will be taken soon or you will be contacted shortly."
    send_email(subject,message,[teacher.user.email])

def email_CEUactivity_approved_by_ISEI(teacher):
    subject = "CEU Activity: " + str(teacher)
    message = str(teacher) + "'s, from " +str(teacher.school.name) + ", CEU activity was approved by ISEI. "
    send_email(subject,message,[teacher.user.email])

def email_CEUactivity_denied_by_ISEI(teacher):
    subject = "CEU Report: " + str(teacher)
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was considered incomplete by the ISEI. Please log in to isei1.org ,review, update and resubmit your CEU Activity."
    send_email(subject,message,[teacher.user.email])

def email_Certificate_issued_or_modified(teacher):
    subject ="ISEI Teacher Certificate"
    message = "Dear " + str(teacher.first_name) +","+"\n " + "Your ISEI Teacher Certification has been issued/renewed/modified. Please log in to isei1.org to view your certification information. If you have any questions, or find any of the information to be innacurate, please contact us."
    send_email(subject, message, [teacher.user.email])
    message1 = str(teacher.first_name) + " from " + str(teacher.school) + " has been issued an ISEI Teacher Certificate."
    send_email(subject, message1, office_email)

def email_Application_submitted(teacher, initial, update, expired):
    subject = str(teacher) + " Application Submitted"
    message = str(teacher) + " from " + str(teacher.school) + " has submitted a Teacher Certification Application."
    if initial:
        if update == True:
            message = message + "\n" + "This is an update to the initial application. No billing is needed"
        else:
            if expired == False:
                message = message + "\n" + "This is an Initial Application, please bill."
            else:
                message = message + "\n" + "This is an update to an expired (no activity for more than 6 months) Initial Application. Please bill."

    else:
        if update == True:
            message = message + "\n" + "This is an update to a Renewal Application. No billing is needed"
        else:
            message = message + "\n" + "This is a Renewal Application, or an update to an expired (no activity for more than 6 months) Renewal Application. Please bill."

    send_email(subject, message, office_email)


def email_Application_processed(teacher):
    subject ="ISEI Teacher Certification Application"
    message = "Dear " + str(teacher.first_name) +","+"\n " + "Your ISEI Teacher Certification Application has been received and your Teacher Certificate will be issued shortly."
    send_email(subject, message, [teacher.user.email])

def email_Application_on_hold(teacher, note = None):
    subject ="ISEI Teacher Certification Application"
    if note:
        message = "Dear " + str(teacher.first_name) +","+"\n " + "Your ISEI Teacher Certification Application has been received and is on hold." + "\n" + str(note) + "\n" + "Please log in to isei1.org if any updates are needed."
    else:
        message = "Dear " + str(teacher.first_name) +","+"\n " + "Your ISEI Teacher Certification Application has been received and will be processed soon."

    send_email(subject, message, [teacher.user.email])
