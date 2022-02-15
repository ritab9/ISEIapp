
from teachercert.models import *

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import unauthenticated_user, allowed_users

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.core.mail import EmailMessage
from django.conf import settings

from .forms import *
from emailing.filters import UserFilter

#send an email to EMAIL_HOST_USER, including message, optional attachment, sender name and email
@login_required(login_url='login')
def ContactISEI(request, userID):

    form_used = EmailFormNoAddress
    sender = Teacher.objects.get(user__id = userID)
    sender_email = User.objects.get(id=userID).email

    if request.method == "GET":
        form = form_used
        return render(request, 'sendemailsattachments.html', {'email_form': form})

    if request.method == "POST":
        form = form_used(request.POST, request.FILES)

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = "From " + str(sender) + '\n' + str(sender_email) + '\n' + '\n' + form.cleaned_data['message']
            files = request.FILES.getlist('attach')
            try:
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, 'sendemailsattachments.html',
                              {'error_message': 'Email sent to ISEI'})

            except:
                return render(request, 'sendemailsattachments.html',
                              {'email_form': form, 'error_message': 'Email was not sent.'})

        return render(request, 'sendemailsattachments.html',
                      {'email_form': form, 'error_message': 'Unable to send email. Please try again later'})




#view that sends an email using a form on a website with mannually entering addresses
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def SendEmailsAttachments(request):

    # TODO need to deal with the cases when user_emails is more than 100. Can't send more than 100 emails at once.
    form_used = EmailFormNoAddress
    users = User.objects.filter(is_active = True)

    #filter
    user_filter =UserFilter(request.GET, queryset=users)
    users = user_filter.qs

    user_emails = users.values_list('email', flat=True)

    if request.method == "GET":
        form = form_used
        return render(request, 'sendemailsattachments.html',
                      {'email_form': form, 'user_emails':user_emails,
                       'user_filter': user_filter})

    if request.method == "POST":
        form = form_used(request.POST, request.FILES)

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            #email = form.cleaned_data['email']
            files = request.FILES.getlist('attach')
            try:
                #BCC all users that receive the message
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, user_emails, ['teacher.certification.isei@gmail.com'] )
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, 'sendemailsattachments.html',
                              {'error_message': 'Sent email to %s' %user_emails})
            except:
                return render(request, 'sendemailsattachments.html',
                              {'email_form': form, 'error_message': 'Unable to send email. Please contact the website administrator'})

        return render(request, 'sendemailsattachments.html',
                      {'email_form': form,
                       'error_message': 'Attachment too big of corrupt',
                        })



# Not used
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def emailing(request):
    # all active teacher
    # teachers = Teacher.objects.filter(user__is_active=True, user__groups__name__in= ['teacher'])
    # principals = Teacher.objects.filter(user__is_active=True, user__groups__name__in= ['principal'])
    #
    #
    # #filter by school
    # school_filter = SchoolFilter(request.GET, queryset=teachers)
    # teachers = school_filter.qs
    # principals = school_filter.qs
    #
    # schools = School.objects.filter(~Q(name__in={'ISEI', 'Sample School'}))
    #
    # today = date.today()
    # in_six_months = today + timedelta(183)
    # a_year_ago = today - timedelta(365)

    if request.method == "GET":
        form = EmailForm
        return render(request, 'sendemailsattachments.html', {'email_form': form})

    if request.method == "POST":
        form = EmailForm(request.POST, request.FILES)

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            files = request.FILES.getlist('attach')
            try:
                mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [email])
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()
                return render(request, 'sendemailsattachments.html',
                              {'error_message': 'Sent email to %s' % email})
            except:
                return render(request, 'sendemailsattachments.html',
                              {'email_form': form, 'error_message': 'Either the attachment is too big or corrupt'})

        return render(request, 'sendemailsattachments.html',
                      {'email_form': form, 'error_message': 'Unable to send email. Please try again later'})
