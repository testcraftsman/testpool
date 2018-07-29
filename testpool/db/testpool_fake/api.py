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
"""
 Holds views for tests results.
"""
# from django.shortcuts import render
import logging

from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.core.exceptions import PermissionDenied
from testpooldb.models import Host
from testpooldb.models import Profile
from testpooldb.models import Resource
from testpool_profile.views import ProfileStats
from testpool_profile.serializers import ProfileSerializer
from testpool_profile.serializers import ProfileStatsSerializer
from testpool_profile.serializers import ResourceSerializer
from testpool_profile.api import JSONResponse
import testpool.core

LOGGER = logging.getLogger("django.testpool")


@csrf_exempt
def profile_add(request, name):
    """ Create a profile .  """

    LOGGER.info("testpool_fake.api.profile_add %s", name)

    if request.method != 'POST':
        msg = "profile_add method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)

    if "resource_max" not in request.GET:
        msg = "profile_add requires resource_max"
        return JsonResponse({"msg": msg}, status=404)

    if "template_name" not in request.GET:
        msg = "profile_add requires template_name"
        return JsonResponse({"msg": msg}, status=404)

    resource_max = request.GET["resource_max"]
    template_name = request.GET["template_name"]

    try:
        resource_max = int(resource_max)
        profile1 = testpool.core.algo.profile_add("localhost", "fake", name,
                                                  resource_max, template_name)
        serializer = ProfileSerializer(profile1)

        return JSONResponse(serializer.data)
    except Profile.DoesNotExist, arg:
        msg = "profile %s not found" % profile_name
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=403)
    except Exception, arg:
        logging.error(arg)
        return JsonResponse({"msg": arg}, status=500)
