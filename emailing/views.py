
from teachercert.models import *

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import unauthenticated_user, allowed_users

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.core import mail
#from django.core.mail import EmailMessage
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




#view that sends an email using a form on a website filtering options for email addresses
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def SendEmailsAttachments(request):
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
            files = request.FILES.getlist('attach')
            try:
                connection = mail.get_connection()
                connection.open()
                for e in user_emails:
                    email = mail.EmailMessage(subject, message, settings.EMAIL_HOST_USER, [e], connection=connection)
                    for f in files:
                        email.attach(f.name, f.read(), f.content_type)
                    email.send()

                #send a copy to ISEI
                message = message + "\n" + "Sent to " + str(list(user_emails))

                email = mail.EmailMessage(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], connection=connection)
                for f in files:
                    email.attach(f.name, f.read(), f.content_type)
                email.send()

                connection.close()
                return render(request, 'sendemailsattachments.html',
                              {'error_message': 'Sent email to %s' %list(user_emails)})
            except:
                return render(request, 'sendemailsattachments.html',
                              {'email_form': form, 'error_message': 'Unable to send email. Please contact the website administrator'})

        return render(request, 'sendemailsattachments.html',
                      {'email_form': form,
                       'error_message': 'Attachment too big or corrupt', })
