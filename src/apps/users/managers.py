import requests
from datetime import timedelta

from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from django.utils.timezone import now
from celery import current_app as celery_app

from common.utils import get_site_url


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **kwargs):
        user = self.model(email=email, name=name, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_testing_user(self, user_data):
        from users.models import TestingUser
        with transaction.atomic():
            lifetime = user_data.pop('lifetime')
            balance = user_data.pop('balance')
            url = '{}/api/v1/users'.format(get_site_url())
            json_data = {
                'name': user_data['name'],
                'confirm_password': user_data['password'],
                'password': user_data['password'],
                'email': user_data['email']
            }

            r = requests.post(url, json=json_data)
            assert r.status_code == 200, 'code: {}, response: {}'.format(r.status_code, r.text)
            user = self.model.objects.get(email=user_data['email'])
            user.role = self.model.REGULAR
            user.is_active = True
            user.activated_at = now()
            user.save()

            celery_app.send_task('users.tasks.FaucetTestingUsersTask', args=[user.id, balance], countdown=3)

            delete_date = now() + timedelta(seconds=int(lifetime))
            TestingUser.objects.create(user_id=user.id, delete_date=delete_date)

        return user

    def get_testing_users(self):
        return self.model.objects.filter(testing_user__isnull=False)

    def delete_expired_testing_users(self):
        current_time = now()
        return self.model.objects.filter(testing_user__delete_date__lte=current_time).filter(testing_user__isnull=False).delete()
