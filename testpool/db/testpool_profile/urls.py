# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testpool
#
# Testbed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Testbed is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Testdb.  If not, see <http://www.gnu.org/licenses/>.
""" URLS profiles. """

from django.conf.urls import url
from . import views
from . import api

# pylint: disable=C0103
urlpatterns = [
    url(r'api/v1/profile/release/(?P<rsrc_id>[\d]+$)', api.profile_release),
    url(r'api/v1/profile/acquire/(?P<profile_name>[\.\w]+$)',
        api.profile_acquire),
    url(r'api/v1/profile/detail/(?P<profile_name>[\.\w]+$)',
        api.profile_detail),
    url(r'api/v1/profile/list', api.profile_list),
    url(r'api/v1/profile/remove/(?P<profile_name>[\.\w]+$)',
        api.profile_remove),
    url(r"view/profile/detail/(?P<profile>.+)", views.detail),
    url(r"view/profiles", views.profile_list),
    url(r"view/dashboard", views.dashboard),
]
