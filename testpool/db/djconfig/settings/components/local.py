
sqllite_path = os.path.join("/var", "tmp", 'db.sqlite3')

RUNSERVER_DEFAULT_PORT = "7000"

print "MARK: local called"

##
# Defines default SQL database
DEFAULT = {
    'ENGINE': 'django.db.backends.sqlite3',
    ##
    # This must point to the sqllite database built from
    # python ./manage.py init
    'NAME': sqllite_path,
}

import sys

DATABASES["local"] = DEFAULT
# Assume if default is defined that this application has been installed
# and so is a release.
if "default" in DATABASES:
    DEBUG = False
else:
    DATABASES["default"] = DEFAULT

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True
