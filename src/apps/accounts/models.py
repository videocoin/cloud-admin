import logging

from django.db import models


logger = logging.getLogger(__name__)


class Account(models.Model):

    id = models.CharField(primary_key=True, max_length=36, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=42, null=True, blank=True)
    key = models.CharField(max_length=512, null=True, blank=True)
    balance = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts'
