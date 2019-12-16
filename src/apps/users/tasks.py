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


class FaucetTestingUsersTask(Task):
    max_retries = 3
    name = 'users.tasks.FaucetTestingUsersTask'

    def run(self, user_id, balance, *args, **kwargs):
        user = User.objects.get(id=user_id)
        r = requests.post(
            settings.FAUCET_URL,
            json={"account": user.address, "amount": int(balance)},
        )
        assert r.status_code == 200, 'code: {}, response: {}'.format(r.status_code, r.text)


celery_app.tasks.register(FaucetTestingUsersTask())
