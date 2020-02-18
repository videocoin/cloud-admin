from __future__ import absolute_import

from datetime import timedelta

from django.utils.timezone import now
from django.conf import settings
from celery import Task
from celery import current_app as celery_app

from streams.blockchain import validate_stream
from streams.models import Stream
from common.utils import send_email, get_site_url


class ValidateStreamsTask(Task):
    max_retries = 3
    name = 'streams.tasks.ValidateStreamsTask'

    def run(self, *args, **kwargs):
        streams = Stream.objects.filter(
            completed_at__gte=now()-timedelta(minutes=settings.STREAM_VALIDATION_FREQUENCY)
        )

        if not streams:
            return
        results = []
        for stream in streams:
            validator = validate_stream(stream)
            validation_results = validator.validate()
            validators = []
            for k, v in validation_results.items():
                if not v.get('is_valid'):
                    validators.append('{}: {}'.format(k, ', '.join(v.get('errors'))))
            if not validator.is_valid or stream.is_failed:
                link = '{}/imsgx72bs1pxd72mxs/streams/stream/{}/change/'.format(
                    get_site_url(), stream.id
                )
                results.append({
                    'id': stream.id,
                    'name': stream.name,
                    'status': stream.get_status_display,
                    'link': link,
                    'validators': validators,
                })
        if results:
            self.send_email(results)

    def send_email(self, results):
        subject = 'VC validations errors'
        send_email(subject, settings.VALIDATION_EMAILS, 'report', {'results': results}, bcc=None)


celery_app.tasks.register(ValidateStreamsTask())
