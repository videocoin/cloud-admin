from project.settings.base import *  # nopep8

DEBUG = False
USE_HTTPS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if 'migrate' in sys.argv:
    # only change this for loaddata command.
    DATABASES['default']['OPTIONS'] = {
       "init_command": "SET foreign_key_checks = 0;",
    }
