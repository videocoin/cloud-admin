from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        super().ready()
        autodiscover_modules('receivers')
