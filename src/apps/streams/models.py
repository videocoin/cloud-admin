import logging
import json
import uuid

from django.db import models
from django_mysql.models import JSONField

from users.models import User
from profiles.models import Profile

logger = logging.getLogger(__name__)


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

    INPUT_TYPE_RTMP = 'INPUT_TYPE_RTMP'
    INPUT_TYPE_WEBRTC = 'INPUT_TYPE_WEBRTC'
    INPUT_TYPE_FILE = 'INPUT_TYPE_FILE'

    INPUT_TYPE_CHOICES = (
        (INPUT_TYPE_RTMP, "RTMP"),
        (INPUT_TYPE_WEBRTC, "WEBRTC"),
        (INPUT_TYPE_FILE, "FILE"),
    )

    OUTPUT_TYPE_HLS = 'OUTPUT_TYPE_HLS'

    OUTPUT_TYPE_CHOICES = (
        (OUTPUT_TYPE_HLS, "HLS"),
    )

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, db_column='user_id')
    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)

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
    deleted_at = models.DateTimeField(null=True, blank=True)

    input_type = models.CharField(max_length=255, choices=INPUT_TYPE_CHOICES, null=True, blank=True)
    output_type = models.CharField(max_length=255, choices=OUTPUT_TYPE_CHOICES, null=True, blank=True)
    
    @property
    def tasks(self):
        return Task.objects.filter(stream_id=str(self.id))

    @property
    def can_be_started(self):
        return self.status in [self.STREAM_STATUS_NONE]

    @property
    def is_failed(self):
        return self.status == self.STREAM_STATUS_FAILED

    @property
    def can_be_stopped(self):
        return self.status in [
            self.STREAM_STATUS_PREPARED,
            self.STREAM_STATUS_PENDING,
            self.STREAM_STATUS_PROCESSING,
            self.STREAM_STATUS_READY
        ]

    class Meta:
        managed = False
        verbose_name = "Stream"
        verbose_name_plural = "Streams"
        ordering = ('-created_at',)
        db_table = 'streams'


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
    machine_type = models.CharField(max_length=255, null=True, blank=True)
    stream = models.ForeignKey(Stream, blank=True, null=True, on_delete=models.CASCADE, db_column='stream_id')

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
    def uri(self):
        return self.input.get('uri', None)

    @property
    def path(self):
        return self.output.get('path', None)

    class Meta:
        managed = False
        db_table = 'tasks'
        ordering = ('-created_at',)


class TaskTransaction(models.Model):

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id', related_name='transactions')
    stream_contract_id = models.CharField(max_length=255, editable=False)
    stream_contract_address = models.CharField(max_length=255, editable=False)
    chunk_id = models.PositiveSmallIntegerField()
    add_input_chunk_tx = models.CharField(max_length=255, null=True, blank=True)
    add_input_chunk_tx_status = models.CharField(max_length=255, null=True, blank=True)
    submit_proof_tx = models.CharField(max_length=255, null=True, blank=True)
    submit_proof_tx_status = models.CharField(max_length=255, null=True, blank=True)
    validate_proof_tx = models.CharField(max_length=255, null=True, blank=True)
    validate_proof_tx_status = models.CharField(max_length=255, null=True, blank=True)
    scrap_proof_tx = models.CharField(max_length=255, null=True, blank=True)
    scrap_proof_tx_status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tasks_tx'
        ordering = ('-created_at',)
