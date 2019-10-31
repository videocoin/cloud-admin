import logging
import json

from django.db import models

from django_mysql.models import JSONField

logger = logging.getLogger(__name__)


class Miner(models.Model):

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    last_ping_at = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    current_task_id = models.CharField(max_length=255, null=True, blank=True)
    tags = JSONField(null=True, blank=True)
    system_info = JSONField(null=True, blank=True)

    @property
    def tags_dict(self):
        if self.tags is None:
            return {}

        if isinstance(self.tags, str):
            self.tags = json.loads(self.tags)

        return self.tags

    @property
    def system_info_dict(self):
        if self.system_info is None:
            return {}

        if isinstance(self.system_info, str):
            self.system_info = json.loads(self.system_info)

        return self.system_info

    @property
    def cpu_freq(self):
        return self.system_info_dict.get('cpu', {}).get('freq')

    @property
    def cpu_cores(self):
        return self.system_info_dict.get('cpu', {}).get('cores')

    @property
    def cpu_usage(self):
        return self.system_info_dict.get('cpu_usage', None)

    @property
    def load1(self):
        return self.system_info_dict.get('load', {}).get('load1')

    @property
    def load5(self):
        return self.system_info_dict.get('load', {}).get('load5')

    @property
    def load15(self):
        return self.system_info_dict.get('load', {}).get('load15')

    @property
    def memory_free(self):
        m = self.system_info_dict.get('memory', {}).get('free')
        if m:
            return round(m / 1024 / 1024 / 1024, 2)

    @property
    def memory_used(self):
        m = self.system_info_dict.get('memory', {}).get('used')
        if m:
            return round(m / 1024 / 1024 / 1024, 2)

    @property
    def memory_total(self):
        m = self.system_info_dict.get('memory', {}).get('total')
        if m:
            return round(m / 1024 / 1024 / 1024, 2)

    class Meta:
        db_table = 'miners'
