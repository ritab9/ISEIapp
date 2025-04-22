from .models import MessageTemplate
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

#not used
def format_text_html(text):
    """Convert plain text with line breaks into email-safe text with <br> tags for HTML emails."""
    return text.replace("\n", "<br>")

#not used
def send_custom_email(template_id, recipient, context):
    """
    Sends an email using a specific template.
    :param template_id: ID of the MessageTemplate to use.
    :param recipient: Email address of the recipient.
    :param context: Dictionary for dynamic placeholders.
    """
    try:
        template = MessageTemplate.objects.get(id=template_id)
        subject, body = template.render(context)

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
        )
    except MessageTemplate.DoesNotExist:
        raise ValueError(f"Template with id {template_id} does not exist.")


def send_simple_email(subject, message, send_to = ["info@iseiea.org"]):
    message = message
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, send_to)
    mail.send()
