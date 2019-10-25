import logging
import json

from django.db import models

from django_mysql.models import JSONField


logger = logging.getLogger(__name__)


class Profile(models.Model):

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    spec = JSONField(null=True, blank=True)

    @property
    def spec_dict(self):
        if self.spec is None:
            return {}

        if isinstance(self.spec, str):
            self.spec = json.loads(self.spec)

        return self.spec

    class Meta:
        db_table = 'profiles'
