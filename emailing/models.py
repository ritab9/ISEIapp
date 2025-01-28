from django.db import models
from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth.models import User


# Step 1: Create the MessageTemplate model
class MessageTemplate(models.Model):
    name = models.CharField(max_length=255)  # Template name for admin identification
    subject = models.CharField(max_length=255)  # Email subject template
    body = models.TextField()  # Email body template with placeholders

    def render(self, context, body_override=None):
        """
        Render the template using the provided context.
        :param context: Dictionary of values to replace placeholders.
        :return: Rendered subject and body as a tuple.
        """
        subject_template = Template(self.subject)
        body_template = Template(body_override or self.body)
        context = Context(context)
        return subject_template.render(context), body_template.render(context)

