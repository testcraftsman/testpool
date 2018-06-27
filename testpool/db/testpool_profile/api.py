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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from testpooldb.models import Profile
from testpooldb.models import Resource
from testpool_profile.views import ProfileStats
from testpool_profile.serializers import ProfileSerializer
from testpool_profile.serializers import ProfileStatsSerializer
from testpool_profile.serializers import ResourceSerializer
import testpool.core.algo

LOGGER = logging.getLogger("django.testpool")


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def profile_list(request):
    """
    List all code snippets, or create a new snippet.
    """

    LOGGER.info("testpool_profile.api.profile_list")

    if request.method == 'GET':
        profiles = [ProfileStats(item) for item in Profile.objects.all()]
        serializer = ProfileStatsSerializer(profiles, many=True)
        return JSONResponse(serializer.data)
    else:
        msg = "profile_list method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def profile_detail(request, profile_name):
    """ Retrieve specific profile.  """

    LOGGER.info("testpool_profile.api.profile_detail")

    try:
        profile = Profile.objects.get(name=profile_name)
    except Profile.DoesNotExist:
        msg = "profile %s not found" % profile_name
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=404)

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return JSONResponse(serializer.data)
    else:
        msg = "profile_detail method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def profile_acquire(request, profile_name):
    """
    Ac_seconds quire a Resource that is ready.

    @param expiration The mount of time in seconds before entry expires.
    """

    LOGGER.info("profile_acquire %s", profile_name)
    if request.method == 'GET':
        expiration_seconds = request.GET.get("expiration", 10 * 60)
        expiration_seconds = int(expiration_seconds)
        try:
            profile = Profile.objects.get(name=profile_name)
        except Profile.DoesNotExist:
            msg = "profile %s not found" % profile_name
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        LOGGER.info("profile_acquire found %s", profile_name)

        try:
            vms = profile.resource_set.filter(status=Resource.READY)

            if vms.count() == 0:
                msg = "profile_acquire %s all resources taken" % profile_name
                LOGGER.info(msg)
                return JsonResponse({"msg": msg}, status=403)
            ##
            # Pick the first resource.
            vm1 = vms[0]
            ##
        except Resource.DoesNotExist:
            msg = "profile %s empty" % profile_name
            LOGGER.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        ##
        # assert vm1 defined.
        vm1.transition(Resource.RESERVED, Resource.ACTION_DESTROY,
                       expiration_seconds)

        ##
        LOGGER.info("profile %s resource acquired %s", profile_name, vm1.name)
        serializer = ResourceSerializer(vm1)
        return JSONResponse(serializer.data)
        ##
    else:
        msg = "profile_acquire method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def profile_release(request, vm_id):
    """ Release Resource. """

    LOGGER.info("testpool_profile.api.profile_release %s", vm_id)

    if request.method == 'GET':
        try:
            vm1 = Resource.objects.get(id=vm_id)
        except Resource.DoesNotExist:
            msg = "profile for %s not found" % vm_id
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        if vm1.status != Resource.RESERVED:
            raise PermissionDenied("Resource %s is not reserved" % vm_id)

        ##
        # assert vm1 defined.
        vm1.transition(Resource.PENDING, Resource.ACTION_DESTROY, 1)
        ##
        content = {"detail": "Resource %s released" % vm_id}

        return JSONResponse(content)
    else:
        msg = "profile_release method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def profile_remove(request, profile_name):
    """ Release Resource. """

    LOGGER.info("testpool_profile.api.profile_remove %s", profile_name)

    if request.method == 'DELETE':
        immediate = request.GET.get("immediate", False)
        try:
            testpool.core.algo.profile_remove(profile_name, immediate)
            content = {"detail": "profile %s removed" % profile_name}
            return JSONResponse(content)
        except Profile.DoesNotExist:
            msg = "profile %s not found" % profile_name
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)
        except Exception as arg:
            logging.error(arg)
            return JsonResponse({"msg": arg}, status=500)
    else:
        msg = "profile_release method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)
