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
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from testpooldb.models import Profile
from testpooldb.models import VM
from profile.views import ProfileStats
from profile.serializers import ProfileSerializer
from profile.serializers import ProfileStatsSerializer
from profile.serializers import VMSerializer



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

    logging.debug("profile list:")

    if request.method == 'GET':
        profiles = [ProfileStats(item) for item in Profile.objects.all()]
        serializer = ProfileStatsSerializer(profiles, many=True)
        return JSONResponse(serializer.data)


@csrf_exempt
def profile_detail(request, pkey):
    """ Retrieve specific profile.  """

    try:
        profile = Profile.objects.get(pk=pkey)
    except Profile.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return JSONResponse(serializer.data)

@csrf_exempt
def profile_acquire(request, name):
    """
    List all code snippets, or create a new snippet.
    """

    logging.debug("profile acquire: %s", name)

    if request.method == 'GET':
        try:
            profile = Profile.objects.get(name=name)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("profile %s not found" % name)

        try:
            vms = profile.vm_set.filter(status=VM.FREE)

            if vms.count() == 0:
                raise serializers.ValidationError("profile %s is full" % name)

            vm1 = vms[0]
            vm1.acquire()

            serializer = VMSerializer(vm1)
            return JSONResponse(serializer.data)
        except VM.DoesNotExist:
            raise serializers.ValidationError("profile %s is full" % name)
