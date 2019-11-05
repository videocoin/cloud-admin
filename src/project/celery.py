import os

from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.staging')

application = Celery('application')
application.config_from_object('django.conf:settings')
application.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@application.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
