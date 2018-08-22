# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
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
from testpooldb.models import Pool
from testpooldb.models import Resource
from testpool_pool.views import PoolStats
from testpool_pool.serializers import PoolSerializer
from testpool_pool.serializers import PoolStatsSerializer
from testpool_pool.serializers import ResourceSerializer
from testpool_pool.api import JSONResponse
import testpool.core

LOGGER = logging.getLogger("django.testpool")


@csrf_exempt
def pool_add(request, name):
    """ Create a pool .  """

    LOGGER.info("testpool_docker.api.pool_add %s", name)

    if request.method != 'POST':
        msg = "pool_add method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)

    if "resource_max" not in request.GET:
        msg = "pool_add requires resource_max"
        return JsonResponse({"msg": msg}, status=404)

    if "template_name" not in request.GET:
        msg = "pool_add requires template_name"
        return JsonResponse({"msg": msg}, status=404)

    resource_max = request.GET["resource_max"]
    template_name = request.GET["template_name"]

    try:
        resource_max = int(resource_max)
        pool1 = testpool.core.algo.pool_add("localhost", "docker", name,
                                            resource_max, template_name)
        serializer = PoolSerializer(pool1)

        return JSONResponse(serializer.data)
    except Pool.DoesNotExist, arg:
        msg = "pool %s not found" % pool_name
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=403)
    except Exception, arg:
        logging.error(arg)
        return JsonResponse({"msg": arg}, status=500)
