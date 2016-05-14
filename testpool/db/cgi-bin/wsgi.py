"""
WSGI config for djconfig project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
import logging

##
# Uncomment this in order to see debug content while Apache2 serves
# content. 
#
#logging.basicConfig(level=logging.DEBUG)
##

##
# Assume the django database is in the same directory as this file.
# If not then change dbsite.
dbsite=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
logging.debug("testbed database directory %s ", dbsite)
sys.path.append(dbsite)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djconfig.settings")
application = get_wsgi_application()
