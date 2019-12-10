import logging
import json
import uuid

from django.db import models

from django_mysql.models import JSONField


logger = logging.getLogger(__name__)


class Profile(models.Model):

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
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

    @property
    def render(self):
        built = ["ffmpeg"]
        built.extend(["-i", "/tmp/in.mp4"])

        for c in self.spec_dict.get('components', {}):
            if not c.get('params'):
                continue
            for i in c.get('params', []):
                built.extend([i.get('key'), i.get('value')])

        built.extend(["$OUTPUT/index.m3u8"])
        return ' '.join(built)

    class Meta:
        managed = False
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        db_table = 'profiles'
