from __future__ import unicode_literals

from django.contrib.auth.models import Permission
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

    def _get_permissions(self, user_obj, obj, from_name):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser or user_obj.is_staff:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            if user_obj.is_superuser:
                setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
            elif user_obj.is_staff:
                return {
                    'users.view_user'
                }

        return getattr(user_obj, perm_cache_name)
