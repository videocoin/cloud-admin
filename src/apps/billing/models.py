import logging
import uuid

from django.db import models

from users.models import User
from profiles.models import Profile
from streams.models import Stream

logger = logging.getLogger(__name__)


class Account(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='billing_accounts')
    email = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.BigIntegerField(default=0)
    customer_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        managed = False
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ('-created_at',)
        db_table = 'billing_accounts'


class Transaction(models.Model):

    TRANSACTION_STATUS_PENDING = 'PENDING'
    TRANSACTION_STATUS_PROCESSING = 'PROCESSING'
    TRANSACTION_STATUS_SUCCESS = 'SUCCESS'
    TRANSACTION_STATUS_FAILED = 'FAILED'
    TRANSACTION_STATUS_CANCELED = 'CANCELED'

    TRANSACTION_STATUS_CHOICES = (
        (TRANSACTION_STATUS_PENDING, "PENDING"),
        (TRANSACTION_STATUS_PROCESSING, "PROCESSING"),
        (TRANSACTION_STATUS_SUCCESS, "SUCCESS"),
        (TRANSACTION_STATUS_FAILED, "FAILED"),
        (TRANSACTION_STATUS_CANCELED, "CANCELED"),
    )

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='from', related_name='transactions_from')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='to', related_name='transactions_to')

    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    status = models.CharField(max_length=255, choices=TRANSACTION_STATUS_CHOICES)

    checked_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)

    payment_intent_secret = models.CharField(max_length=255, null=True, blank=True)
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=255, null=True, blank=True)

    stream = models.ForeignKey(Stream, null=True, blank=True, on_delete=models.SET_NULL, db_column='stream_id')
    stream_name = models.CharField(max_length=255, null=True, blank=True)
    stream_contract_address = models.CharField(max_length=255, null=True, blank=True)
    stream_is_live = models.BooleanField(default=False)

    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, db_column='profile_id')
    profile_name = models.CharField(max_length=255, null=True, blank=True)
    profile_cost = models.DecimalField(max_digits=10, decimal_places=4)

    task_id = models.CharField(max_length=255, null=True, blank=True)
    chunk_num = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        managed = False
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ('-created_at',)
        db_table = 'billing_transactions'

