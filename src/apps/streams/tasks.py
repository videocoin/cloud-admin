from __future__ import absolute_import

import logging
from datetime import timedelta

from django.utils.timezone import now
from celery import Task
from celery import current_app as celery_app
from django.conf import settings

from videocoin.blockchain import Blockchain
from videocoin.validators import ValidatorCollection
from streams.models import Stream
from common.utils import send_email, get_site_url
logger = logging.getLogger(__name__)


class ValidateStreamsTask(Task):
    max_retries = 3
    name = 'streams.tasks.ValidateStreamsTask'

    def run(self, *args, **kwargs):
        streams = Stream.objects.filter(completed_at__gte=now()-timedelta(minutes=settings.STREAM_VALIDATION_FREQUENCY))

        if not streams:
            return
        results = []
        for stream in streams:
            blockchain = Blockchain(
                settings.RPC_NODE_HTTP_ADDR,
                stream_id=stream.stream_contract_id,
                stream_address=stream.stream_contract_address,
                stream_manager_address=settings.STREAM_MANAGER_CONTRACT_ADDR
            )

            events = blockchain.get_all_events()
            validator = ValidatorCollection(
                events=events,
                input_url=stream.input_url,
                output_url=stream.output_url
            )
            validation_results = validator.validate()
            if not validator.is_valid or stream.is_failed:
                results.append({
                    'id': stream.id,
                    'name': stream.name,
                    'status': stream.status,
                    'link': '{}/imsgx72bs1pxd72mxs/streams/stream/{}/change/'.format(get_site_url(), stream.id),
                    'validators': ', '.join([k for k, v in validation_results.items() if not v.get('is_valid')]),
                })
        if results:
            self.send_email(results)

    def send_email(self, results):
        subject = 'VC validations errorr'
        send_email(subject, settings.VALIDATION_EMAILS, 'report', {'results': results}, bcc=None)


celery_app.tasks.register(ValidateStreamsTask())
