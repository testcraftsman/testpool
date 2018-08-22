# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
""" URLS pools. """

from django.conf.urls import url
from . import views
from . import api

# pylint: disable=C0103
urlpatterns = [
    url(r'api/v1/pool/release/(?P<rsrc_id>[\d]+$)', api.pool_release),
    url(r'api/v1/pool/acquire/(?P<pool_name>[\.\w]+$)',
        api.pool_acquire),
    url(r'api/v1/pool/detail/(?P<pool_name>[\.\w]+$)',
        api.pool_detail),
    url(r'api/v1/pool/list', api.pool_list),
    url(r'api/v1/pool/remove/(?P<pool_name>[\.\w]+$)',
        api.pool_remove),
    url(r'api/v1/pool/add/(?P<pool_name>[\.\w]+$)',
        api.pool_add),
    url(r"view/pool/detail/(?P<pool>.+)", views.detail),
    url(r"view/pools", views.pool_list),
    url(r"view/dashboard", views.dashboard),
]
