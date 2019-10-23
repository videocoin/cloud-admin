from project.settings.base import *  # nopep8

DEBUG = False
USE_HTTPS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
