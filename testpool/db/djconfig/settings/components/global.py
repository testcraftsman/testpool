import logging
import os

##
# Provides location of plain text file that defines the mysql connection
# information. The existance of the mysql configuration file implies that
# it will become default database.
CONF = "/etc/testpool/testpool.yml"
# WSGI_APPLICATION = 'cgi-bin.wsgi.application'

sqllite_path = os.path.join("/var", "tmp", 'testpooldb.sqlite3')

if os.path.exists(CONF):
    DEFAULT_PORT = "8001"
    logging.debug("loading %s" % CONF)
    DEBUG = False
    DATABASES["global"] = {
        'ENGINE': 'django.db.backends.sqlite3',
        ##
        # This must point to the sqllite database built from
        # python ./manage.py init
        'NAME': sqllite_path,
    }
    DATABASES["default"] = DATABASES["global"]

    STATIC_ROOT = os.path.join("/usr", "local", "testpool", "static")
