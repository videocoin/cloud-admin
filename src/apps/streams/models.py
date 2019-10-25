import logging
import json

from django.db import models

from django_mysql.models import JSONField

from users.models import User
from profiles.models import Profile

logger = logging.getLogger(__name__)


class Task(models.Model):

    CREATED = 'CREATED'
    PENDING = 'PENDING'
    ASSIGNED = 'ASSIGNED'
    ENCODING = 'ENCODING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'

    STATUS_CHOICES = (
        (CREATED, "CREATED"),
        (PENDING, "PENDING"),
        (ASSIGNED, "ASSIGNED"),
        (ENCODING, "ENCODING"),
        (COMPLETED, "COMPLETED"),
        (FAILED, "FAILED"),
        (CANCELED, "CANCELED"),
    )

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    owner_id = models.IntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=CREATED)
    profile_id = models.CharField(max_length=36)
    cmdline = models.TextField(null=True, blank=True)
    input = JSONField(null=True, blank=True)
    output = JSONField(null=True, blank=True)
    client_id = models.CharField(max_length=255, editable=False, null=True, blank=True)
    stream_contract_id = models.BigIntegerField(null=True, blank=True)
    stream_contract_address = models.CharField(max_length=255, editable=False, null=True, blank=True)

    @property
    def can_be_stopped(self):
        return self.status in [self.PENDING, self.ASSIGNED, self.ENCODING]

    @property
    def input_dict(self):
        if self.input is None:
            return {}

        if isinstance(self.input, str):
            self.input = json.loads(self.input)

        return self.input

    @property
    def output_dict(self):
        if self.output is None:
            return {}

        if isinstance(self.output, str):
            self.output = json.loads(self.output)

        return self.output

    @property
    def render(self):
        p = Profile.objects.get(id=str(self.profile_id))
        built = ["ffmpeg"]

        if p.name == "test":
            input = "/tmp/in.mp4"
        else:
            input = self.input_dict.get('uri')
        built.extend(["-i", input])

        for c in p.spec_dict.get('components', {}):
            if not c.get('params'):
                continue
            for i in c.get('params', []):
                built.extend([i.get('key'), i.get('value')])
        output = self.output_dict.get('path')

        output += "/index.m3u8"

        built.extend([output])
        return ' '.join(built)

    class Meta:
        db_table = 'tasks'


class Stream(models.Model):
    STREAM_STATUS_NONE = 0
    STREAM_STATUS_NEW = 1
    STREAM_STATUS_PREPARING = 2
    STREAM_STATUS_PREPARED = 3
    STREAM_STATUS_PENDING = 4
    STREAM_STATUS_PROCESSING = 5
    STREAM_STATUS_READY = 6
    STREAM_STATUS_COMPLETED = 7
    STREAM_STATUS_CANCELLED = 8
    STREAM_STATUS_FAILED = 9

    STREAM_STATUS_CHOICES = (
        (STREAM_STATUS_NONE, "None"),
        (STREAM_STATUS_NEW, "New"),
        (STREAM_STATUS_PREPARING, "Preparing"),
        (STREAM_STATUS_PREPARED, "Prepared"),
        (STREAM_STATUS_PENDING, "Pending"),
        (STREAM_STATUS_PROCESSING, "Processing"),
        (STREAM_STATUS_READY, "Ready"),
        (STREAM_STATUS_COMPLETED, "Completed"),
        (STREAM_STATUS_CANCELLED, "Cancelled"),
        (STREAM_STATUS_FAILED, "Failed"),
    )

    INPUT_STATUS_NONE = 0
    INPUT_STATUS_PENDING = 1
    INPUT_STATUS_ACTIVE = 2
    INPUT_STATUS_ERROR = 3

    INPUT_STATUS_CHOICES = (
        (INPUT_STATUS_NONE, "None"),
        (INPUT_STATUS_PENDING, "Pending"),
        (INPUT_STATUS_ACTIVE, "Active"),
        (INPUT_STATUS_ERROR, "Error"),
    )

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    profile_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=STREAM_STATUS_CHOICES, null=True, blank=True)
    input_status = models.IntegerField(choices=INPUT_STATUS_CHOICES, null=True, blank=True)
    stream_contract_id = models.BigIntegerField(null=True, blank=True)
    stream_contract_address = models.CharField(max_length=255, editable=False, null=True, blank=True)

    input_url = models.URLField(max_length=255, null=True, blank=True)
    output_url = models.URLField(max_length=255, null=True, blank=True)
    rtmp_url = models.URLField(max_length=255, null=True, blank=True)

    refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def user(self):
        return User.objects.get(id=str(self.user_id))

    @property
    def task(self):
        return Task.objects.get(id=str(self.id))

    @property
    def task_id(self):
        return self.task.id

    @property
    def task_status(self):
        return self.task.status

    @property
    def task_cmdline(self):
        return self.task.cmdline

    @property
    def task_input(self):
        return self.task.input

    @property
    def task_output(self):
        return self.task.output

    @property
    def task_can_be_stopped(self):
        return self.task.can_be_stopped

    @property
    def task_render(self):
        return self.task.render

    class Meta:
        db_table = 'streams'
