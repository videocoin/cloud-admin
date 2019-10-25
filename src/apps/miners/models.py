import logging

from django.db import models

logger = logging.getLogger(__name__)


class Miner(models.Model):

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'miners'
