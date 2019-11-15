import logging
import uuid

from django.db import models

from users.models import User

logger = logging.getLogger(__name__)


class Transfer(models.Model):
    TRANSFER_KIND_NONE = 0
    TRANSFER_KIND_WITHDRAW = 1

    TRANSFER_KIND_CHOICES = (
        (TRANSFER_KIND_NONE, "None"),
        (TRANSFER_KIND_WITHDRAW, "Withdraw"),
    )

    TRANSFER_STATUS_NONE = 0
    TRANSFER_STATUS_NEW = 1
    TRANSFER_STATUS_PENDING_NATIVE = 2
    TRANSFER_STATUS_EXECUTED_NATIVE = 3
    TRANSFER_STATUS_PENDING_ERC = 4
    TRANSFER_STATUS_COMPLETED = 5
    TRANSFER_STATUS_FAILED = 6

    TRANSFER_STATUS_CHOICES = (
        (TRANSFER_STATUS_NONE, "None"),
        (TRANSFER_STATUS_NEW, "New"),
        (TRANSFER_STATUS_PENDING_NATIVE, "Pending native"),
        (TRANSFER_STATUS_EXECUTED_NATIVE, "Executed_native"),
        (TRANSFER_STATUS_PENDING_ERC, "Pending erc"),
        (TRANSFER_STATUS_COMPLETED, "Completed"),
        (TRANSFER_STATUS_FAILED, "Failed"),
    )

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=36)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    pin = models.CharField(max_length=6, null=True, blank=True)
    kind = models.IntegerField(choices=TRANSFER_KIND_CHOICES, null=True, blank=True)
    status = models.IntegerField(choices=TRANSFER_STATUS_CHOICES, null=True, blank=True)
    to_address = models.CharField(max_length=255, null=True, blank=True)
    amount = models.CharField(max_length=255, null=True, blank=True)
    tx_native_id = models.CharField(max_length=255, null=True, blank=True)
    tx_erc20_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        db_table = 'transfers'
