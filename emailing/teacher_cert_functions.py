
from teachercert.models import *

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import unauthenticated_user, allowed_users

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.core.mail import EmailMessage, send_mass_mail
from django.conf import settings

from .forms import *
from emailing.filters import UserFilter


signature = "\n" + "\n" + "ISEI Teacher Certification" + "\n" + "www.isei1.org"

def send_email(subject, message, to = None):
    message = message+signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, cc=["teacher.certification.isei@gmail.com"])
    mail.send()


def email_AcademicClass_submitted(teacher):
    subject = "Academic Class: " + str(teacher)
    message = str(teacher) + " from " +str(teacher.school.name) + " has submitted an academic class. www.isei1.org "
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, cc =["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_created(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = str(teacher) + " from " +str(teacher.school.name) + " has initiated a CEU Report for the " + school_year_name + " school year. www.isei1.org"
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, cc =["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_submitted(teacher, principal_emails, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = str(teacher) + " from " +str(teacher.school.name) + " has submitted a CEU Report for the " + school_year_name + " school year. Log in to www.isei1.org in order to review and approve the CEU Report. ISEI will NOT receive the report unless you review it. "
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, principal_emails, cc =["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_approved_by_principal(teacher,school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message1 = str(teacher) + "'s, from " +str(teacher.school.name) + ",  " + school_year_name + " CEU Report was approved by the principal. Log in to www.isei1.org in order to review and approve the CEU Report. "
    message1 = message1 + signature
    mail1 = (subject, message1, settings.EMAIL_HOST_USER, ["teacher.certification.isei@gmail.com"])
    message2 = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was signed by the principal and submitted to ISEI. It will be reviewed shortly."
    message2 = message2 + signature
    mail2 = (subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email],["teacher.certification.isei@gmail.com"])
    send_mass_mail((mail1, mail2), fail_silently= False)

def email_CEUReport_denied_by_principal(teacher,school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was considered incomplete by the principal. Please log in to isei1.org ,review, update and resubmit your Report."
    message =message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER,[teacher.user.email], cc =  ["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_retracted_by_principal(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) + "," + "\n " + "The principal has canceled the previous action on your CEU Report. If a new action is not taken soon, please contact your principal."
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [teacher.user.email],
                        cc = ["teacher.certification.isei@gmail.com"])
    mail.send()


def email_CEUactivity_approved_by_principal(teacher):
    subject = "CEU Activity: " + str(teacher)
    message1 = str(teacher) + "'s, from " +str(teacher.school.name) + ", CEU activity was approved by the principal. Log in to www.isei1.org in order to review and approve the CEU Activity. "
    message1 = message1 + signature
    mail1 = (subject, message1, settings.EMAIL_HOST_USER, ["teacher.certification.isei@gmail.com"])
    message2 = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was signed by the principal and submitted to ISEI. It will be reviewed shortly."
    message2 = message2 + signature
    mail2 = (subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email], ["teacher.certification.isei@gmail.com"])
    send_mass_mail((mail1, mail2), fail_silently= False)


def email_CEUactivity_denied_by_principal(teacher):
    subject = "CEU Report: " + str(teacher)
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was considered incomplete by the principal. Please log in to isei1.org ,review, update and resubmit your CEU Activity."
    message =message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER,[teacher.user.email], cc = ["teacher.certification.isei@gmail.com"])
    mail.send()



def email_CEUReport_approved_by_ISEI(teacher,school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was reviewed by ISEI. Please sign in to isei1.org to review the approved activities and CEUs."
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [teacher.user.email], cc = ["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_denied_by_ISEI(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU Report was considered incomplete by ISEI. Please log in to isei1.org ,review, update and resubmit your Report."
    message =message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER,[teacher.user.email], cc =  ["teacher.certification.isei@gmail.com"])
    mail.send()

def email_CEUReport_retracted_by_ISEI(teacher, school_year_name):
    subject = "CEU Report: " + str(teacher) + ", " + school_year_name
    message = "Dear " + str(teacher.first_name) + "," + "\n " + "ISEI has canceled the previous action on your CEU Report. A new action will be taken soon or you will be contacted shortly."
    message = message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [teacher.user.email],
                        cc = ["teacher.certification.isei@gmail.com"])
    mail.send()


def email_CEUactivity_approved_by_principal(teacher):
    subject = "CEU Activity: " + str(teacher)
    message1 = str(teacher) + "'s, from " +str(teacher.school.name) + ", CEU activity was approved by the principal. Log in to www.isei1.org in order to review and approve the CEU Activity. "
    message1 = message1 + signature
    mail1 = (subject, message1, settings.EMAIL_HOST_USER, ["teacher.certification.isei@gmail.com"])
    message2 = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was signed by the principal and submitted to ISEI. It will be reviewed shortly."
    message2 = message2 + signature
    mail2 = (subject, message2, settings.EMAIL_HOST_USER, [teacher.user.email], ["teacher.certification.isei@gmail.com"])
    send_mass_mail((mail1, mail2), fail_silently= False)


def email_CEUactivity_denied_by_principal(teacher):
    subject = "CEU Report: " + str(teacher)
    message = "Dear " + str(teacher.first_name) +","+"\n "+ "Your CEU activity was considered incomplete by the principal. Please log in to isei1.org ,review, update and resubmit your CEU Activity."
    message =message + signature
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER,[teacher.user.email], cc = ["teacher.certification.isei@gmail.com"])
    mail.send()