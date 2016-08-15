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
from rest_framework import serializers
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from testpooldb.models import Profile
from testpooldb.models import VM
from testpool_profile.views import ProfileStats
from testpool_profile.serializers import ProfileSerializer
from testpool_profile.serializers import ProfileStatsSerializer
from testpool_profile.serializers import VMSerializer

logger = logging.getLogger("django.testpool")


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

    logger.info("testpool_profile.api.profile_list")

    if request.method == 'GET':
        profiles = [ProfileStats(item) for item in Profile.objects.all()]
        serializer = ProfileStatsSerializer(profiles, many=True)
        return JSONResponse(serializer.data)


@csrf_exempt
def profile_detail(request, pkey):
    """ Retrieve specific profile.  """

    logger.info("testpool_profile.api.profile_detail")

    try:
        profile = Profile.objects.get(pk=pkey)
    except Profile.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return JSONResponse(serializer.data)

@csrf_exempt
def profile_acquire(request, profile_name):
    """
    Acquire a VM that is ready.
    """

    logger.info("testpool_profile.api.profile_acquire %s", profile_name)

    if request.method == 'GET':
        try:
            profile = Profile.objects.get(name=profile_name)
        except Profile.DoesNotExist:
            raise serializers.ValidationError(
                "profile %s not found" % profile_name)

        try:
            vms = profile.vm_set.filter(status=VM.FREE)

            if vms.count() == 0:
                raise serializers.ValidationError(
                    "profile %s is full" % profile_name)

            vm1 = vms[0]
            vm1.acquire()

            serializer = VMSerializer(vm1)
            return JSONResponse(serializer.data)
        except VM.DoesNotExist:
            raise serializers.ValidationError(
                "profile %s is full" % profile_name)

@csrf_exempt
def profile_release(request, vm_id):
    """ Release VM. """

    logger.info("testpool_profile.api.profile_release %s", vm_id)

    if request.method == 'GET':
        try:
            vm1 = VM.objects.get(id=vm_id)
        except VM.DoesNotExist:
            raise serializers.ValidationError("VM %s does not exist" % vm_id)

        if vm1.status != VM.RESERVED:
            raise serializers.ValidationError("VM %s not reserved" % vm_id)

        vm1.release()
        content = {"msg": "VM %s released" % vm_id}
        return Response(content, status=status.HTTP_200_OK)
