# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
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
from testpooldb.models import Pool
from testpooldb.models import Resource
from testpool_pool.views import PoolStats
from testpool_pool.serializers import PoolSerializer
from testpool_pool.serializers import PoolStatsSerializer
from testpool_pool.serializers import ResourceSerializer
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
def pool_list(request):
    """
    List all code snippets, or create a new snippet.
    """

    LOGGER.info("testpool_pool.api.pool_list")

    if request.method == 'GET':
        pools = [PoolStats(item) for item in Pool.objects.all()]
        serializer = PoolStatsSerializer(pools, many=True)
        return JSONResponse(serializer.data)
    else:
        msg = "pool_list method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def pool_detail(request, pool_name):
    """ Retrieve specific pool.  """

    LOGGER.info("testpool_pool.api.pool_detail")

    try:
        pool = Pool.objects.get(name=pool_name)
    except Pool.DoesNotExist:
        msg = "pool %s not found" % pool_name
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=404)

    if request.method == "GET":
        serializer = PoolSerializer(pool)
        return JSONResponse(serializer.data)
    else:
        msg = "pool_detail method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def pool_acquire(request, pool_name):
    """
    Ac_seconds quire a Resource that is ready.

    @param expiration The mount of time in seconds before entry expires.
    """

    LOGGER.info("pool_acquire %s", pool_name)
    if request.method == 'GET':
        expiration_seconds = request.GET.get("expiration", 10 * 60)
        expiration_seconds = int(expiration_seconds)
        try:
            pool = Pool.objects.get(name=pool_name)
        except Pool.DoesNotExist:
            msg = "pool %s not found" % pool_name
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        LOGGER.info("pool_acquire found %s", pool_name)

        try:
            rsrcs = pool.resource_set.filter(status=Resource.READY)

            if rsrcs.count() == 0:
                msg = "pool_acquire %s all resources taken" % pool_name
                LOGGER.info(msg)
                return JsonResponse({"msg": msg}, status=403)
            ##
            # Pick the first resource.
            rsrc = rsrcs[0]
            ##
        except Resource.DoesNotExist:
            msg = "pool %s empty" % pool_name
            LOGGER.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        ##
        # assert resource defined.
        rsrc.transition(Resource.RESERVED, Resource.ACTION_DESTROY,
                        expiration_seconds)

        ##
        LOGGER.info("pool %s resource acquired %s", pool_name, rsrc.name)
        serializer = ResourceSerializer(rsrc)
        return JSONResponse(serializer.data)
        ##
    else:
        msg = "pool_acquire method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def pool_release(request, rsrc_id):
    """ Release Resource. """

    LOGGER.info("testpool_pool.api.pool_release %s", rsrc_id)

    if request.method == 'GET':
        try:
            rsrc = Resource.objects.get(id=rsrc_id)
        except Resource.DoesNotExist:
            msg = "pool for %s not found" % rsrc_id
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)

        if rsrc.status != Resource.RESERVED:
            raise PermissionDenied("Resource %s is not reserved" % rsrc_id)

        ##
        # assert rsrc defined.
        rsrc.transition(Resource.PENDING, Resource.ACTION_DESTROY, 1)
        ##
        content = {"detail": "Resource %s released" % rsrc_id}

        return JSONResponse(content)
    else:
        msg = "pool_release method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def pool_remove(request, pool_name):
    """ Release Resource. """

    LOGGER.info("testpool_pool.api.pool_remove %s", pool_name)

    if request.method == 'DELETE':
        immediate = request.GET.get("immediate", False)
        try:
            testpool.core.algo.pool_remove(pool_name, immediate)
            content = {"detail": "pool %s removed" % pool_name}
            return JSONResponse(content)
        except Pool.DoesNotExist:
            msg = "pool %s not found" % pool_name
            logging.error(msg)
            return JsonResponse({"msg": msg}, status=403)
        except Exception as arg:
            logging.error(arg)
            return JsonResponse({"msg": arg}, status=500)
    else:
        msg = "pool_release method %s unsupported" % request.method
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=405)


@csrf_exempt
def pool_add(request, pool_name):
    """ Add a pool .  """

    LOGGER.info("testpool_pool.api.pool_add %s", pool_name)

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

    if "connection" not in request.GET:
        msg = "pool_add requires connection"
        return JsonResponse({"msg": msg}, status=404)

    if "product" not in request.GET:
        msg = "pool_add requires product"
        return JsonResponse({"msg": msg}, status=404)

    resource_max = request.GET["resource_max"]
    template_name = request.GET["template_name"]
    connection = request.GET["connection"]
    product = request.GET["product"]

    try:
        resource_max = int(resource_max)
        pool1 = testpool.core.algo.pool_add(connection, product, pool_name,
                                            resource_max, template_name)
        serializer = PoolSerializer(pool1)

        return JSONResponse(serializer.data)
    except Pool.DoesNotExist, arg:
        logging.exception(arg)
        msg = "pool %s not found" % pool_name
        logging.error(msg)
        return JsonResponse({"msg": msg}, status=403)
    except Exception, arg:
        logging.exception(arg)
        logging.error(arg)
        return JsonResponse({"msg": arg}, status=500)
