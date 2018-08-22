# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
"""
URLS for Host content.
"""
from django.conf.urls import url
from . import api


# pylint: disable=C0103
urlpatterns = [
    url(r'api/v1/resource/renew/(?P<rsrc_id>[\d]+$)', api.resource_renew),
]
