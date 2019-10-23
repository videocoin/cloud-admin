from project.settings.base import *  # nopep8

DEBUG = False
USE_HTTPS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#
# if SENTRY_DSN:
#     INSTALLED_APPS += (
#         'raven.contrib.django.raven_compat',
#     )
#
#     RAVEN_CONFIG = {
#         'dsn': SENTRY_DSN,
#     }
#
#     LOGGING['handlers']['sentry'] = {
#             'level': 'ERROR',
#             'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
#     }
#
#     for key, logger, in LOGGING['loggers'].items():
#         logger['handlers'].append('sentry')

if 'migrate' in sys.argv:
    # only change this for loaddata command.
    DATABASES['default']['OPTIONS'] = {
       "init_command": "SET foreign_key_checks = 0;",
    }
