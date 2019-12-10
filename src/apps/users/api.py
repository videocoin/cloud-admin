import json

import shortuuid

from django.http import JsonResponse
from django.views.generic import View

from .models import User


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
