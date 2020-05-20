from __future__ import absolute_import

import logging
import requests

from django.conf import settings
from celery import Task
from celery import current_app as celery_app

from users.models import User


logger = logging.getLogger(__name__)


class CleanupTestingUsersTask(Task):
    max_retries = 3
    name = 'users.tasks.CleanupTestingUsersTask'

    def run(self, *args, **kwargs):
        User.objects.delete_expired_testing_users()


celery_app.tasks.register(CleanupTestingUsersTask())
