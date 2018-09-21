import os
import sys


RUNSERVER_DEFAULT_PORT = "7000"

##
# Defines default SQL database
DEFAULT = {
    'ENGINE': 'django.db.backends.sqlite3',
    ##
    # This must point to the sqllite database built from
    # python ./manage.py init
    'NAME': os.path.join("/tmp", 'testpooldb.sqlite3'),
}

if "test" not in sys.argv:
    DATABASES["local"] = DEFAULT
    # Assume if default is defined that this application has been installed
    # and so is a release.
    if "default" not in DATABASES:
        DATABASES["default"] = DEFAULT
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
