import json

import shortuuid

from django.http import JsonResponse
from django.views.generic import View
from django.utils.timezone import now
from celery import current_app as celery_app

from .models import User, TestingUser


class UserAPIView(View):

    def get_default_user_data(self):
        id = shortuuid.ShortUUID().random(length=22)
        password = shortuuid.ShortUUID().random(length=12)
        return {
            'email': 'testing{}@liveplanet.net'.format(id),
            'name': 'Test User #{}'.format(id),
            'password': password,
            'lifetime': 86400,
            'balance': 10,
        }

    def get(self, request):
        users = User.objects.get_testing_users()
        return JsonResponse([{
            'email': u.email,
            'name': u.name,
        } for u in users], safe=False, status=200)

    def post(self, request):
        user_data = self.get_default_user_data()
        if request.body:
            user_data.update(json.loads(request.body))
        resp = user_data.copy()
        u = User.objects.create_testing_user(user_data)
        return JsonResponse({
            'id': u.id,
            'email': resp.get('email'),
            'password': resp.get('password'),
            'name': resp.get('name'),
            'lifetime': resp.get('lifetime'),
            'balance': resp.get('balance'),
        }, status=200)


class UsersAPIView(View):

    def get_default_user_data(self):
        id = shortuuid.ShortUUID().random(length=22)
        password = shortuuid.ShortUUID().random(length=12)
        return {
            'email': 'testing{}@liveplanet.net'.format(id),
            'name': 'Test User #{}'.format(id),
            'password': password,
            'lifetime': 86400,
            'balance': 10,
        }

    def post(self, request):
        count = 10
        lifetime = 86400
        balance = 10
        if request.body:
            request_data = json.loads(request.body)
            count = request_data.get('count', count)
            lifetime = request_data.get('lifetime', lifetime)
            balance = request_data.get('balance', balance)
        user_datas = [self.get_default_user_data() for x in range(count)]
        resp = []
        for user_data in user_datas:
            user_data['lifetime'] = lifetime
            user_data['balance'] = balance
            u = User.objects.create_testing_user(user_data)
            resp.append({
                'id': u.id,
                'email': user_data.get('email'),
                'password': user_data.get('password'),
                'name': user_data.get('name'),
                'lifetime': lifetime,
                'balance': balance,
            })
        return JsonResponse(resp, safe=False, status=200)


class ManageUserAPIView(View):

    def put(self, request, id):
        if request.body:
            request_data = json.loads(request.body)
        user = User.objects.filter(id=id).first()
        if not user or not user.is_testing:
            return JsonResponse({'error': 'Not found'}, status=404)
        balance, lifetime = None, None
        if request_data.get('balance'):
            balance = request_data.pop('balance')
        if request_data.get('lifetime'):
            lifetime = request_data.pop('lifetime')

        User.objects.filter(id=id).update(**request_data)

        if balance:
            celery_app.send_task('users.tasks.FaucetTestingUsersTask', args=[user.id, balance], countdown=3)
        if lifetime:
            User.objects.update_lifetime(id, lifetime)
        return JsonResponse({}, status=200)

    def delete(self, request, id):
        user = User.objects.filter(id=id).first()
        if not user or not user.is_testing:
            return JsonResponse({'error': 'Not found'}, status=404)
        User.objects.filter(id=id).delete()

        return JsonResponse({}, status=204)

    def get(self, request, id):
        user = User.objects.filter(id=id).first()
        if not user or not user.is_testing:
            return JsonResponse({'error': 'Not found'}, status=404)

        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'name': user.name,
        }, status=200)
