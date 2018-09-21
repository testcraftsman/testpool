import logging
import os

##
# This is the production configuration when testpool is installed.

##
# Provides location of plain text file that defines the mysql connection
# information. The existance of the mysql configuration file implies that
# it will become default database.
CONF = "/etc/testpool/testpool.yml"
# WSGI_APPLICATION = 'cgi-bin.wsgi.application'

if os.path.exists(CONF):
    DEFAULT_PORT = "8000"
    #  DEBUG = False
    DEBUG = True
    DATABASES["global"] = {
        'ENGINE': 'django.db.backends.sqlite3',
        ##
        # This must point to the sqllite database built from
        # python ./manage.py init
        'NAME': os.path.join("/var", "tmp", 'testpooldb.sqlite3')
    }
    DATABASES["default"] = DATABASES["global"]

    STATICFILES_DIRS = (
      '/var/lib/testpool/static',
    )
