import functools
import warnings
import decimal

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from .tasks import send_email_task


def send_email(subject, recipients_email, template, context=None, bcc=None):
    """
    simple async sending email
    """
    if not context:
        context = {}
    html_content = render_to_string('emails/{}.html'.format(template), context)
    if isinstance(recipients_email, (list, tuple)):
        task = send_email_task.apply_async(args=[subject, recipients_email, html_content, bcc])
    else:
        task = send_email_task.apply_async(args=[subject, [recipients_email], html_content, bcc])

    return task.id


def get_site_url():
    """
    Return site url. Set it in django admin
    """
    current_site = Site.objects.get_current().domain
    if settings.USE_HTTPS:
        return 'https://' + current_site
    return 'http://' + current_site


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)

    return new_func


def to_two_prec_decimal(d_value):
    d_value = decimal.Decimal(d_value)
    if d_value != 0 and d_value < decimal.Decimal('0.01'):
        return d_value.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_UP)
    return d_value.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_UP)


def to_two_prec_decimal_string(d_value):
    return str(to_two_prec_decimal(d_value))
