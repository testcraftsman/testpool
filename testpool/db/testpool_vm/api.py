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
from testpooldb.models import VM
from testpool_profile.serializers import VMSerializer
from testpool.core import algo

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
def vm_renew(request, vm_id):
    """
    Renew a VM currently held for testing.

    @param expiration The mount of time in seconds before VM expires.
    """

    LOGGER.info("profile_renew %s", vm_id)
    if request.method == 'GET':
        expiration_seconds = int(request.GET.get("expiration", 10*60))
        LOGGER.info("expiration in seconds %s", expiration_seconds)

        try:
            vm1 = VM.objects.get(id=vm_id)
            LOGGER.info("VM %s found", vm1.name)
        except VM.DoesNotExist:
            raise Http404("VM %s not found" % vm_id)

        ##
        # assert vm1 defined.
        vm1.transition(VM.RESERVED, algo.ACTION_DESTROY, expiration_seconds)

        serializer = VMSerializer(vm1)
        return JSONResponse(serializer.data)
        ##

    else:
        logging.error("profile_acquire method %s unsupported", request.method)
