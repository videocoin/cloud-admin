import logging

from django.db import models

from users.models import User

logger = logging.getLogger(__name__)


class Account(models.Model):

    id = models.CharField(primary_key=True, max_length=36, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=42, null=True, blank=True)
    key = models.CharField(max_length=512, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'accounts'
