
# Standard Library Imports
from django.conf import settings

# Django Utilities
#from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import linebreaksbr
#from django.utils.html import format_html, escape
from django.views.decorators.csrf import csrf_exempt

# Project-specific Decorators
from users.decorators import allowed_users

# Forms and Filters
from .forms import *
from emailing.filters import UserFilter

# Models
from .models import MessageTemplate
from teachercert.models import *
from selfstudy.models import SelfStudy, SelfStudy_TeamMember
from accreditation.models import Standard

# Functions
#from .functions import format_text_html
from .teacher_cert_functions import email_registered_user


#not used
#def send_custom_email(request, template_id):
#    template = get_object_or_404(MessageTemplate, id=template_id)
#    if request.method == "POST":
#        form = EmailForm(request.POST)
#        if form.is_valid():
#            subject = form.cleaned_data['subject']
#            body = form.cleaned_data['body']
#            recipient = request.POST.get('recipient')  # Assume recipient is passed in the POST request
# Send the email
#            send_mail(
#                subject=subject,
#                message=body,
#                from_email='your_email@example.com',
#                recipient_list=[recipient],
#            )
#           return HttpResponse("Email sent successfully!")
#    else:
# Pre-fill the form with the template's content
#        subject, body = template.render({})
#        form = EmailForm(initial={"subject": subject, "body": body})
#    return render(request, "send_email.html", {"form": form, "template": template})


def send_email_selfstudy_coordinating_team(request, selfstudy_id):
    selfstudy = get_object_or_404(SelfStudy, id=selfstudy_id)
    standards=Standard.objects.top_level()
    team_members = SelfStudy_TeamMember.objects.filter(team__selfstudy=selfstudy).distinct('user')
    # Prepare the email template and context
    template = get_object_or_404(MessageTemplate, name='SelfStudy Coordinating Team Invitation')

    # Collect email data to display for preview(subject and body rendered once)
    example_email = None
    other_recipients = []
    for member in team_members:
        user = member.user
        # Display data for one user, send name and email for everyone else
        if not example_email:
            context = {'user': user}
            subject, body = template.render(context)  # Render the subject and body for the member
            example_email =({
                'subject': subject,
                'body': body,
                'recipient': user.email,
                'full_name': user.get_full_name(),
            })
        else:
            other_recipients.append({'email': user.email,'full_name': user.get_full_name(),})

    if request.method == 'POST':
        failed_recipients = []  # Track failed sends
        selected_recipients = request.POST.getlist('recipients') # Get the selected recipients

        # Get the edited body content from the form if it exists
        override = request.POST.get('override') == 'true'
        edited_body = request.POST.get('edited_body') if override else None

        for member in team_members:
            user = member.user
            if str(user.id) in selected_recipients:
                context = {'user': user}
                # Render subject and body, using the edited content if provided
                subject, body = template.render(context, body_override=edited_body)
                try:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=linebreaksbr(body),
                    )
                except Exception as e:
                    failed_recipients.append(member.user.email)  # Track failures

        #if failed_recipients:
        #    messages.error(request,
        #        f"Failed to send emails to the following recipients: {', '.join(failed_recipients)}.")
        #else:
        #    messages.success(request, "All emails were sent successfully!")

        return redirect('selfstudy_coordinating_team', selfstudy_id=selfstudy.id)

    context=dict(selfstudy=selfstudy, standards=standards,
                 example_email=example_email, other_recipients=other_recipients,
                 template_body=template.body,
                 team_members=team_members,)

    return render(request, 'send_email_selfstudy_coordinating_team.html', context)



#TeacherCert emailing views
#TODO rewrite all this using the send_custom_email view and send_custom_email funtion from functions

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

@csrf_exempt
def email_registered_user_view(request, teacherID):
    if request.method == 'POST':
        teacher = Teacher.objects.get(id=teacherID)
        email_registered_user(teacher)  # Call your function here
        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'failed'}, status=400)

