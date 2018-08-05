# (c) 2016 Mark Hamilton, <mark.lee.hamilton@gmail.com>
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
"""
View profile information.
"""
import json
import logging
from django.shortcuts import render_to_response
from testpooldb import models

LOGGER = logging.getLogger("django.testpool")


# pylint: disable=R0902
# pylint: disable=R0903
class ProfileStats(object):
    """ Provides individual profile stats used in the profile view. """

    def __init__(self, profile):
        """Contruct a profile view. """

        ##
        # pylint: disable=C0103
        # The ID is needed for the JSON view.
        self.id = profile.id
        #
        self.connection = profile.host.connection
        self.name = profile.name
        self.resource_max = profile.resource_max
        self.vm_ready = 0
        self.vm_reserved = 0
        self.vm_pending = 0
        self.vm_bad = 0

        for item in models.Resource.objects.filter(profile=profile):
            if item.status == models.Resource.RESERVED:
                self.vm_reserved += 1
            elif item.status == models.Resource.PENDING:
                self.vm_pending += 1
            elif item.status == models.Resource.READY:
                self.vm_ready += 1
            elif item.status == models.Resource.BAD:
                self.vm_bad += 1


def profile_list(_):
    """ Summarize product information. """
    LOGGER.debug("profile")

    profiles = models.Profile.objects.all()
    profiles = [ProfileStats(item) for item in profiles]

    html_data = {"profiles": profiles}
    return render_to_response("profile/list.html", html_data)


def detail(_, profile):
    """ Provide profile details. """

    LOGGER.debug("profile/detail/%s", profile)

    profile1 = models.Profile.objects.get(name=profile)
    vms = [item for item in models.Host.objects.filter(profile=profile1)]
    html_data = {
        "vms": vms,
        "profile": profile1
    }

    return render_to_response("profile/detail.html", html_data)


def dashboard(_):
    """ Provide summary of all profiles. """

    LOGGER.debug("views.dashboard")

    return render_to_response('profile/index.html')
