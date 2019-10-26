import os
import environ


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
)

LOCAL_APPS = (
    'common',
    'base',
    'users',
    'streams',
    'profiles',
    'miners',
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

# project settings
USE_HTTPS = False

SENTRY_DSN = env.str('VC_ADMIN_SENTRY_DSN', None)
if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

    LOGGING['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }

    for key, logger, in LOGGING['loggers'].items():
        logger['handlers'].append('sentry')