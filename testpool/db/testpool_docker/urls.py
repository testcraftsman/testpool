# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
""" URLS pools. """

from django.conf.urls import url
from . import api

# pylint: disable=C0103
urlpatterns = [
    url(r'api/v1/pool/add/docker/(?P<name>.+)', api.pool_add),
]
