from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **kwargs):
        user = self.model(email=email, name=name, **kwargs)
        user.set_password(password)
        user.save()

        return user


