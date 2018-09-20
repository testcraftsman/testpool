import os
import sys

sqllite_path = os.path.join("/var", "tmp", 'testpooldb.sqlite3')

RUNSERVER_DEFAULT_PORT = "7000"

##
# Defines default SQL database
DEFAULT = {
    'ENGINE': 'django.db.backends.sqlite3',
    ##
    # This must point to the sqllite database built from
    # python ./manage.py init
    'NAME': sqllite_path,
}

if "test" not in sys.argv and not os.path.exists(CONF):
    DATABASES["local"] = DEFAULT
    # Assume if default is defined that this application has been installed
    # and so is a release.
    if "default" not in DATABASES:
        DATABASES["default"] = DEFAULT
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    print "MARK: local 2", STATIC_ROOT
