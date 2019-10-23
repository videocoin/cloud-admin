from __future__ import unicode_literals

from passlib.hash import bcrypt

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as DjangoModelBackend


UserModel = get_user_model()


class ModelBackend(DjangoModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if not bcrypt.using(rounds=12, ident='2a', salt=None).verify(password, user.password):
                return
            if not user.is_staff:
                return
            request._cached_user = user
            return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(id=str(user_id))
            if user.is_active:
                return user
            return None
        except UserModel.DoesNotExist:
            return None
