from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection


logger = get_task_logger('mail')


# JOBS EMAIL =========================================================================
@shared_task(bind=True)
def send_email_task(self, subject, recipient_emails, html_content, bcc=None):   # pylint: disable=unused-argument
    connection = get_connection()
    messages = []
    for recipient_email in recipient_emails:
        if bcc:  # sendgrid fix
            email = EmailMultiAlternatives(
                subject, html_content, settings.DEFAULT_FROM_EMAIL, bcc=bcc
            )
        else:
            email = EmailMultiAlternatives(
                subject, html_content, settings.DEFAULT_FROM_EMAIL
            )
        email.attach_alternative(html_content, "text/html")
        email.to = [recipient_email]
        messages.append(email)

    connection.send_messages(messages)
