import os
import environ
from datetime import timedelta

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)

env_file = os.getenv("VC_ADMIN_ENV_FILE", None)

if env_file is None:
    environ.Env.read_env()
else:
    environ.Env.read_env(env_file)


import sys
from django.utils.translation import ugettext_lazy as _


SITE_ROOT = root()
sys.path.append(os.path.join(SITE_ROOT, 'apps'))
sys.path.append(os.path.join(SITE_ROOT, 'libs'))

DEBUG = env('VC_ADMIN_DEBUG')
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': env.db('VC_ADMIN_DATABASE_URL', engine='django.db.backends.mysql')
}

SECRET_KEY = env('VC_ADMIN_SECRET_KEY')

ALLOWED_HOSTS = ['*']

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

THIRDPARTY_APPS = (
    'django_mysql',
    'prettyjson',
    'jsoneditor',
)

LOCAL_APPS = (
    'common',
    'base',
    'users',
    'streams',
    'profiles',
    'miners',
    'accounts',
    'transfers',
)

DEPRECATED_APPS = ()

INSTALLED_APPS = DJANGO_APPS + THIRDPARTY_APPS + LOCAL_APPS + DEPRECATED_APPS

SITE_ID = 1


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (
    os.path.join(SITE_ROOT, 'conf', 'locale'),
)
LANGUAGES = [
    ('en', _('English'))
]
USE_TZ = True

STATIC_URL = env.str('VC_ADMIN_STATIC_URL', '/imsgx72bs1pxd72mxs/assets/')
STATIC_ROOT = os.path.join(SITE_ROOT, 'assets')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'static'),
)

APPEND_SLASH = False

DJANGO_LOG_LEVEL = env.str('VC_ADMIN_LOGLEVEL', 'INFO')

BROKER_URL = env.str('VC_ADMIN_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = \
    env.str('VC_ADMIN_CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')

STREAM_VALIDATION_FREQUENCY = 5  # minutes

CELERYBEAT_SCHEDULE = {
    'cleanup-testing-users': {
        'task': 'users.tasks.CleanupTestingUsersTask',
        'schedule': timedelta(seconds=3600)
    },
    'validate-streams': {
        'task': 'streams.tasks.ValidateStreamsTask',
        'schedule': timedelta(seconds=STREAM_VALIDATION_FREQUENCY * 60)
    },
}
VALIDATION_EMAILS = env.str('VC_ADMIN_VALIDATION_EMAILS', '').split(';')

DEFAULT_LOGGER = {
    'handlers': ['console'],
    'level': DJANGO_LOG_LEVEL,
}

DEFAULT_JSON_LOGGER = {
    'handlers': ['json_console'],
    'level': DJANGO_LOG_LEVEL,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(asctime)s %(name)s %(message)s'
        },
        'short': {
            'format': '[%(levelname)s] %(asctime)s %(message)s'
        },
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'json_verbose': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)s %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'json_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'loggers': {
        'django': DEFAULT_LOGGER,
        'celery': DEFAULT_LOGGER,
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SITE_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
            ],
            'debug': DEBUG,
        },
    },
]

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'users.backends.ModelBackend',
]

USE_HTTPS = True

JSON_EDITOR_INIT_JS = "jsoneditor-init.js"

TESTING_USER_EMAILS = [
    'videocointtest@yandex.com',
    'videocointtest@yandex.ru',
]
EMAIL_HOST = env.str('VC_ADMIN_EMAIL_HOST', None)
EMAIL_HOST_USER = env.str('VC_ADMIN_EMAIL_USER', None)
EMAIL_HOST_PASSWORD = env.str('VC_ADMIN_EMAIL_PASSWORD', None)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str('VC_ADMIN_DEFAULT_FROM_EMAIL', None)

SENTRY_DSN = env.str('VC_ADMIN_SENTRY_DSN', None)

FAUCET_URL = env.str('VC_ADMIN_FAUCET_URL', '').strip()

PRIVATE_STREAMS_RPC_ADDR = env.str('VC_ADMIN_PRIVATE_STREAMS_RPC_ADDR', None)

SYMPHONY_KEY_FILE = env.str('VC_ADMIN_SYMPHONY_KEY_FILE', '')
SYMPHONY_OAUTH2_CLIENTID = env.str('VC_ADMIN_SYMPHONY_OAUTH2_CLIENTID', '')
SYMPHONY_ADDR = env.str('VC_ADMIN_SYMPHONY_ADDR', '')

STREAM_MANAGER_CONTRACT_ADDR = env.str('VC_ADMIN_STREAM_MANAGER_CONTRACT_ADDR').strip()

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
