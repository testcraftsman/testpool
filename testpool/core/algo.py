"""
   Algorithm for modifying database.
"""
import sys
import logging
import traceback
from testpooldb import models
import testpool.core.api


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


def adapt(pool, profile):
    """ Adapt the pool to the profile size.

    @return Returns the number of changes. Positive number indicates the
            number of resources created.
    """
    logging.debug("%s: adapt started", profile.name)

    changes = 0

    ##
    # Check the database for the list of existing and pending virtual
    # items.
    current = profile.resource_set.count()

    ##
    if current == profile.resource_max:
        return changes
    elif current > profile.resource_max:
        ##
        # Too many resources we need to remove one.
        how_many = current - profile.resource_max
        for rsrc in profile.resource_set.reverse():
            if rsrc.status in [models.Resource.READY, models.Resource.PENDING]:
                rsrc.transition(models.Resource.PENDING, ACTION_DESTROY, 1)
                how_many -= 1

            if how_many <= 0:
                break
    else:
        ##
        # there are not enough resources. Add more. current represents
        # the next slot so add that to count.
        for count in range(profile.resource_max):
            changes += 1
            name = pool.new_name_get(profile.template_name, count+current)
            logging.info("%s checking", name)
            (rsrc, _) = models.Resource.objects.get_or_create(profile=profile,
                                                              name=name)
            state = pool.state_get(name)
            logging.debug("%s status %s", name, state)
            if state == testpool.core.api.Pool.STATE_NONE:
                logging.debug("%s expanding pool resource with %s ",
                              profile.name, name)
                rsrc.transition(models.Resource.PENDING, ACTION_CLONE, 1)
    return changes


def clone(pool, rsrc):
    """ Clone a resource. """

    pool.clone(rsrc.profile.template_name, rsrc.name)
    state = pool.start(rsrc.name)
    logging.debug("%s resource clone state %s", rsrc.profile.name, state)

    if state != testpool.core.api.Pool.STATE_RUNNING:
        logging.error("%s resource clone %s failed", rsrc.profile.name,
                      rsrc.name)
        rsrc.transition(models.Resource.BAD, ACTION_DESTROY, 1)
    else:
        logging.debug("%s resource cloned %s", rsrc.profile.name, rsrc.name)
        rsrc.transition(models.Resource.PENDING, ACTION_ATTR, 1)


def attr(pool, rsrc):
    """ Retrieve resource attributes. """

    rsrc.ip_addr = pool.ip_get(rsrc.name)
    for (key, value) in pool.resource_attr_get(rsrc.name).iteritems():
        (kvp, _) = models.KVP.get_or_create(key, value)
        models.ResourceKVP.objects.create(resource=rsrc, kvp=kvp)
        rsrc.transition(models.Resource.READY, ACTION_STATUS, 10*60)


def destroy(pool, profile):
    """ Reset profile and remove all resources from the host. """

    for rsrc in profile.resource_set.all():
        name = rsrc.name
        logging.debug("%s removing resource %s", profile.name, name)

        state = pool.state_get(name)
        if state != testpool.core.api.Pool.STATE_NONE:
            pool.destroy(name)

        try:
            rsrc = models.Resource.objects.get(profile=profile, name=name)
            rsrc.delete()
        except models.Resource.DoesNotExist:
            pass


def pop(profile_name, expiration_seconds):
    """ Pop one resource from the Pool. """

    logging.info("algo.pop resource from %s", profile_name)

    profile1 = models.Profile.objects.get(name=profile_name)
    rsrcs = models.Resource.objects.filter(profile=profile1,
                                           status=models.Resource.PENDING)

    if rsrcs.count() == 0:
        raise NoResources("%s: all resources taken" % profile_name)

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

    pool.clone(rsrc.profile.template_name, rsrc.name)
    pool.start(rsrc.name)
    rsrc.transition(models.Resource.PENDING, testpool.core.algo.ACTION_ATTR, 1)


def resource_destroy(pool, rsrc):
    """ Destroy a single resource. """

    name = rsrc.name
    logging.debug("%s removing resource %s", rsrc.profile.name, name)

    state = pool.state_get(name)
    if state != testpool.core.api.Pool.STATE_NONE:
        pool.destroy(name)

    if rsrc.profile.resource_set.all().count() > rsrc.profile.resource_max:
        try:
            rsrc.delete()
        except models.Resource.DoesNotExist:
            pass
