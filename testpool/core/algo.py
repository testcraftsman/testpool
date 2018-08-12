"""
   Algorithm for modifying database.
"""
import sys
import logging
import traceback
from testpooldb import models
import testpool.core.api
import testpool.core.ext


ACTION_ATTR = "attr"
ACTION_CLONE = "clone"
ACTION_DESTROY = models.Resource.ACTION_DESTROY
ACTION_STATUS = "status"
ACTION_NONE = "none"


class ResourceReleased(Exception):
    """ Resource already relased. """

    def __init__(self, value):
        """ Name of resource. """
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        """ Return the name of the resource. """
        return repr(self.value)


class NoResources(Exception):
    """ Resource does not exist. """

    def __init__(self, value):
        """ Name of resource. """
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        """ Return the name of the resource. """
        return repr(self.value)


def onerror(name):
    """ Show module that fails to load. """

    logging.error("importing module %s", name)
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)


def adapt(pool_api, pool):
    """ Adapt the pool to the pool size.

    @return Returns the number of changes. Positive number indicates the
            number of resources created.
    """
    logging.debug("%s: adapt started", pool.name)

    changes = 0

    ##
    # Check the database for the list of existing and pending virtual
    # items.
    current = pool.resource_set.count()

    ##
    if current == pool.resource_max:
        return changes
    elif current > pool.resource_max:
        key = testpool.core.api.Pool.TIMING_REQUEST_DESTROY
        delta = pool_api.timing_get(key)
        ##
        # Too many resources we need to remove one.
        how_many = current - pool.resource_max
        for rsrc in pool.resource_set.reverse():
            if rsrc.status in [models.Resource.READY, models.Resource.PENDING]:
                rsrc.transition(models.Resource.PENDING, ACTION_DESTROY, delta)
                how_many -= 1

            if how_many <= 0:
                break
    else:
        missing = pool.resource_max - current
        logging.debug("%s: adapt too few make %d more", pool.name, missing)
        ##
        # There are not enough resources. Try to reuse the range of
        # names from 0 to resource_max. Start at 0 and walk up the range
        # looking for free slots.
        for count in range(pool.resource_max):
            name = pool_api.new_name_get(pool.template_name, count)
            logging.info("%s checking", name)
            (rsrc, action) = models.Resource.objects.get_or_create(pool=pool,
                                                                   name=name)

            if not action:
                # This is an existing resource. Keep looking
                continue

            state = pool_api.state_get(name)
            logging.debug("%s status %s", name, state)

            # If action is true then the database entry was just created.
            # If state == STATE_NONE then this name does not exist.
            if state == testpool.core.api.Pool.STATE_NONE:
                # This is a new database entry and the resource does
                # not exist. Clone this.
                logging.debug("%s expanding pool resource with %s ", pool.name,
                              name)
                key = testpool.core.api.Pool.TIMING_REQUEST_CLONE
                delta = pool_api.timing_get(key)
                rsrc.transition(models.Resource.PENDING, ACTION_CLONE, delta)
                changes += 1
                missing -= 1
            else:
                logging.warning("%s: lost track of resource %s reclaiming",
                                pool.name, rsrc.name)
                ##
                # Need to destroy the resource because we do not know its
                # real state.
                key = testpool.core.api.Pool.TIMING_REQUEST_DESTROY
                delta = pool_api.timing_get(key)
                rsrc.transition(models.Resource.PENDING, ACTION_DESTROY, delta)
                ##
                changes += 1
                missing -= 1

            if missing == 0:
                break
    return changes


def clone(pool_api, rsrc):
    """ Clone a resource. """

    pool_api.clone(rsrc.pool.template_name, rsrc.name)
    state = pool_api.start(rsrc.name)
    logging.debug("%s resource clone state %s", rsrc.pool.name, state)

    if state != testpool.core.api.Pool.STATE_RUNNING:
        logging.error("%s resource clone %s failed", rsrc.pool.name,
                      rsrc.name)
        key = testpool.core.api.Pool.TIMING_REQUEST_DESTROY
        delta = pool_api.timing_get(key)
        rsrc.transition(models.Resource.BAD, ACTION_DESTROY, delta)
    else:
        logging.debug("%s resource cloned %s", rsrc.pool.name, rsrc.name)
        delta = pool_api.timing_get(testpool.core.api.Pool.TIMING_REQUEST_ATTR)
        rsrc.transition(models.Resource.PENDING, ACTION_ATTR, delta)


def attr(pool_api, rsrc):
    """ Retrieve resource attributes. """

    rsrc.ip_addr = pool_api.ip_get(rsrc.name)
    for (key, value) in pool_api.resource_attr_get(rsrc.name).iteritems():
        (kvp, _) = models.KVP.get_or_create(key, value)
        models.ResourceKVP.objects.create(resource=rsrc, kvp=kvp)
        rsrc.transition(models.Resource.READY, ACTION_STATUS, 10*60)


def destroy(pool_api, pool):
    """ Reset pool and remove all resources from the host. """

    for rsrc in pool.resource_set.all():
        name = rsrc.name
        logging.debug("%s removing resource %s", pool.name, name)

        state = pool_api.state_get(name)
        if state != testpool.core.api.Pool.STATE_NONE:
            pool_api.destroy(name)

        try:
            rsrc = models.Resource.objects.get(pool=pool, name=name)
            rsrc.delete()
        except models.Resource.DoesNotExist:
            pass


def pop(pool_name, expiration_seconds):
    """ Pop one resource from the Pool. """

    logging.info("algo.pop resource from %s", pool_name)

    pool1 = models.Pool.objects.get(name=pool_name)
    rsrcs = models.Resource.objects.filter(pool=pool1,
                                           status=models.Resource.PENDING)

    if rsrcs.count() == 0:
        raise NoResources("%s: all resources taken" % pool_name)

    rsrc = rsrcs[0]
    rsrc.transition(models.Resource.RESERVED, ACTION_DESTROY,
                    expiration_seconds)
    rsrc.status = models.Resource.RESERVED
    rsrc.save()

    return rsrc


def push(rsrc_id):
    """ Push one resource by id. """

    logging.info("push %d", rsrc_id)
    try:
        rsrc = models.Resource.objects.get(id=rsrc_id,
                                           status=models.Resource.RESERVED)
        rsrc.release()
        return 0
    except models.Resource.DoesNotExist:
        raise ResourceReleased(rsrc_id)


def resource_clone(pool, rsrc):
    """ Reclaim a resource and rebuild it. """

    logging.debug("reclaiming %s", rsrc.name)

    pool.clone(rsrc.pool.template_name, rsrc.name)
    pool.start(rsrc.name)
    delta = pool.timing_get(testpool.core.api.Pool.TIMING_REQUEST_ATTR)
    rsrc.transition(models.Resource.PENDING, ACTION_ATTR, delta)


def resource_destroy(pool, rsrc):
    """ Destroy a single resource. """

    name = rsrc.name
    logging.debug("%s removing resource %s", rsrc.pool.name, name)

    state = pool.state_get(name)
    if state == testpool.core.api.Pool.STATE_NONE:
        ##
        # actual resource is gone.
        rsrc.delete()
        ##
    else:
        pool.destroy(name)
        ##
        # Attempted to destroy the resource. Check back some later time.
        delta = pool.timing_get(testpool.core.api.Pool.TIMING_REQUEST_DESTROY)
        rsrc.transition(rsrc.status, rsrc.action, delta)
        ##


def pool_add(connection, product, pool, resource_max, template):
    """ Add a pool. """

    logging.debug("pool_add %s %s", pool, template)
    (host1, _) = models.Host.objects.get_or_create(connection=connection,
                                                   product=product)
    defaults = {"resource_max": resource_max, "template_name": template}
    (pool1, _) = models.Pool.objects.update_or_create(name=pool, host=host1,
                                                      defaults=defaults)
    ##
    # Check to see if the number of Resources should change.
    exts = testpool.core.ext.api_ext_list()
    pool = exts[product].pool_get(pool1)
    adapt(pool, pool1)
    ##
    return pool1


def pool_remove(name, immediate):
    """ Remove a pool.

    Pools can't be removed immediately, Resources are marked for purge
    and when all Resources are gone the pool will be removed.
    """

    pool = models.Pool.objects.get(name=name)
    logging.debug("found pool %s", pool)
    pool.resource_max = 0
    pool.save()

    next_delta = 0
    for rsrc in pool.resource_set.all():
        if immediate:
            rsrc.delete()
        else:
            rsrc.transition(models.Resource.RESERVED, ACTION_DESTROY,
                            next_delta)
            next_delta += 60

    if immediate:
        pool.delete()
