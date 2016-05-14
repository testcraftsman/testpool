import logging

##
# Provides location of plain text file that defines the mysql connection
# information. The existance of the mysql configuration file implies that
# it will become default database.
MYSQL_CNF="/usr/local/testbed/etc/mysql.cnf"
WSGI_APPLICATION = 'cgi-bin.wsgi.application'

if os.path.exists(MYSQL_CNF):
    logging.debug("loading mysql %s" % MYSQL_CNF)
    DEBUG = False
    DATABASES["global"] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testbed',
        'init_command': 'Set storage_engine=INNODB',
        'OPTIONS': {
            'read_default_file': MYSQL_CNF
        }
    }
    DATABASES["default"] = DATABASES["global"]

    STATIC_ROOT = os.path.join("/usr", "local", "testbed", "static")
