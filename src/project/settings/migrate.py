from project.settings.base import *  # nopep8

DEBUG = False

AUTH_USER_MODEL = 'auth.User'

if 'migrate' in sys.argv:
    # only change this for loaddata command.
    DATABASES['default']['OPTIONS'] = {
       "init_command": "SET foreign_key_checks = 0;",
    }
