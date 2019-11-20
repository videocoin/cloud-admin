import logging
import uuid

from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager,  AbstractBaseUser, PermissionsMixin

logger = logging.getLogger(__name__)


class User(PermissionsMixin, AbstractBaseUser):
    REGULAR = 0
    QA = 3
    MANAGER = 6
    SUPER = 9

    ROLES_CHOICES = (
        (REGULAR, "Regular"),
        (QA, "QA"),
        (MANAGER, "Manager"),
        (SUPER, "Super"),
    )

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    email = models.EmailField(unique=True, max_length=255, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)

    role = models.IntegerField(choices=ROLES_CHOICES)

    last_login = None
    is_superuser = True
    groups = []
    user_permissions = []
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = BaseUserManager()

    def natural_key(self):
        return (self.get_username(), )

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    @property
    def is_staff(self):
        return self.role in [self.MANAGER, self.SUPER]

    @property
    def is_superuser(self):
        return self.role in [self.SUPER]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    @property
    def account(self):
        from accounts.models import Account
        return Account.objects.filter(user_id=str(self.id)).first()

    @property
    def balance(self):
        if self.account:
            return str(int(self.account.balance_wei) / 10**18)

    @property
    def address(self):
        if self.account:
            return self.account.address

    class Meta:
        ordering = ('-created_at',)
        db_table = 'users'


class ApiToken(models.Model):

    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=36)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        db_table = 'user_api_tokens'
