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
from testpooldb.models import Resource
from testpool_pool.serializers import ResourceSerializer

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
def resource_renew(request, rsrc_id):
    """
    Renew a Resource currently held for testing.

    @param expiration The mount of time in seconds before Resource expires.
    """

    LOGGER.info("profile_renew %s", rsrc_id)
    if request.method == 'GET':
        expiration_seconds = int(request.GET.get("expiration", 10*60))
        LOGGER.info("expiration in seconds %s", expiration_seconds)

        try:
            rsrc = Resource.objects.get(id=rsrc_id)
            LOGGER.info("Resource %s found", rsrc.name)
        except Resource.DoesNotExist:
            raise Http404("Resource %s not found" % rsrc_id)

        ##
        # assert rsrc defined.
        rsrc.transition(Resource.RESERVED, Resource.ACTION_DESTROY,
                        expiration_seconds)

        serializer = ResourceSerializer(rsrc)
        return JSONResponse(serializer.data)
        ##
    else:
        logging.error("profile_acquire method %s unsupported", request.method)
        raise Http404("profile_release method only get supported")
