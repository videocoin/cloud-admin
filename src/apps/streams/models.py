import logging
import json
import uuid

from django.db import models
from django.utils.html import format_html
from django_mysql.models import JSONField

from users.models import User

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

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
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

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, null=True, blank=True)
    profile_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=STREAM_STATUS_CHOICES, null=True, blank=True)
    input_status = models.IntegerField(choices=INPUT_STATUS_CHOICES, null=True, blank=True)
    stream_contract_id = models.BigIntegerField(null=True, blank=True)
    stream_contract_address = models.CharField(max_length=255, editable=False, null=True, blank=True)

    input_url = models.CharField(max_length=255, null=True, blank=True)
    output_url = models.CharField(max_length=255, null=True, blank=True)
    rtmp_url = models.CharField(max_length=255, null=True, blank=True)

    refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def get_rtmp_url(self):
         return format_html('<a target="_blank" href="{}" />Link</a>', self.rtmp_url)
    get_rtmp_url.short_description = "RTMP"

    def get_input_url(self):
         return format_html('<a target="_blank" href="{}" />Link</a>', self.input_url)
    get_input_url.short_description = "Input"

    def get_output_url(self):
         return format_html('<a target="_blank" href="{}" />Link</a>', self.output_url)
    get_output_url.short_description = "Output"

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
        return self.task.input.get('uri', None)

    @property
    def task_output(self):
        return self.task.output.get('path', None)

    @property
    def task_can_be_stopped(self):
        return self.task.can_be_stopped

    @property
    def task_client_id(self):
        return self.task.client_id

    @property
    def can_be_started(self):
        return self.status in [self.STREAM_STATUS_NONE]

    @property
    def can_be_stopped(self):
        return self.status in [
            self.STREAM_STATUS_PREPARING,
            self.STREAM_STATUS_PREPARED,
            self.STREAM_STATUS_PENDING,
            self.STREAM_STATUS_PROCESSING,
            self.STREAM_STATUS_READY
        ]

    class Meta:
        ordering = ('-created_at',)
        db_table = 'streams'
