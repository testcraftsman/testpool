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


def vm_name_create(template, count):
    """ Generate resource name based on template. """

    return template + ".%d" % count


def adapt(vmpool, profile):
    """ Adapt the pool to the profile size.

    @return Returns the number of changes. Positive number indicates the
            number of resources created.
    """
    logging.debug("%s: adapt started", profile.name)

    changes = 0

    ##
    # Check the database for the list of existing and pending virtual
    # items.
    vm_current = profile.resource_set.count()

    ##
    if vm_current == profile.vm_max:
        return changes
    elif vm_current > profile.vm_max:
        how_many = vm_current - profile.vm_max
        for vm1 in profile.resource_set.reverse():
            if vm1.status in [models.Resource.READY, models.Resource.PENDING]:
                vm1.transition(models.Resource.PENDING, ACTION_DESTROY, 1)
                how_many -= 1

            if how_many <= 0:
                break
    else:
        ##
        # there are not enough resources. Add more. vm_current represents
        # the next slot so add that to count.
        for count in range(profile.vm_max):
            changes += 1
            vm_name = vmpool.new_name_get(profile.template_name,
                                          count+vm_current)
            logging.info("%s checking", vm_name)
            (vm1, _) = models.Resource.objects.get_or_create(profile=profile,
                                                             name=vm_name)
            vm_state = vmpool.state_get(vm_name)
            logging.debug("%s status %s", vm_name, vm_state)
            if vm_state == testpool.core.api.Pool.STATE_NONE:
                logging.debug("%s expanding pool resource with %s ",
                              profile.name, vm_name)
                vm1.transition(models.Resource.PENDING, ACTION_CLONE, 1)
    return changes


def clone(vmpool, vm1):
    """ Clone a resource. """

    vmpool.clone(vm1.profile.template_name, vm1.name)
    vm_state = vmpool.start(vm1.name)
    logging.debug("%s resource clone state %s", vm1.profile.name, vm_state)

    if vm_state != testpool.core.api.Pool.STATE_RUNNING:
        logging.error("%s resource clone %s failed", vm1.profile.name,
                      vm1.name)
        vm1.transition(models.Resource.BAD, ACTION_DESTROY, 1)
    else:
        logging.debug("%s resource cloned %s", vm1.profile.name, vm1.name)
        vm1.transition(models.Resource.PENDING, ACTION_ATTR, 1)


def attr(vmpool, vm1):
    """ Retrieve resource attributes. """

    vm1.ip_addr = vmpool.ip_get(vm1.name)
    for (key, value) in vmpool.vm_attr_get(vm1.name).iteritems():
        (kvp, _) = models.KVP.get_or_create(key, value)
        models.ResourceKVP.objects.create(vm=vm1, kvp=kvp)
        vm1.transition(models.Resource.READY, ACTION_STATUS, 10*60)


def destroy(vmpool, profile):
    """ Reset profile and remove all resources from the host. """

    for vm1 in profile.resource_set.all():
        vm_name = vm1.name
        logging.debug("%s removing resource %s", profile.name, vm_name)

        vm_state = vmpool.state_get(vm_name)
        if vm_state != testpool.core.api.Pool.STATE_NONE:
            vmpool.destroy(vm_name)

        try:
            vm1 = models.Resource.objects.get(profile=profile, name=vm_name)
            vm1.delete()
        except models.Resource.DoesNotExist:
            pass


def pop(profile_name, expiration_seconds):
    """ Pop one resource from the Pool. """

    logging.info("algo.pop resource from %s", profile_name)

    profile1 = models.Profile.objects.get(name=profile_name)
    vms = models.Resource.objects.filter(profile=profile1,
                                         status=models.Resource.PENDING)

    if vms.count() == 0:
        raise NoResources("%s: all resources taken" % profile_name)

    vm1 = vms[0]
    vm1.transition(models.Resource.RESERVED, ACTION_DESTROY,
                   expiration_seconds)
    vm1.status = models.Resource.RESERVED
    vm1.save()

    return vm1


def push(vm_id):
    """ Push one resource by id. """

    logging.info("push %d", vm_id)
    try:
        vm1 = models.Resource.objects.get(id=vm_id,
                                          status=models.Resource.RESERVED)
        vm1.release()
        return 0
    except models.Resource.DoesNotExist:
        raise ResourceReleased(vm_id)


def vm_clone(vmpool, vmh):
    """ Reclaim a resource and rebuild it. """

    logging.debug("reclaiming %s", vmh.name)

    vmpool.clone(vmh.profile.template_name, vmh.name)
    vmpool.start(vmh.name)
    vmh.transition(models.Resource.PENDING, testpool.core.algo.ACTION_ATTR, 1)


def vm_destroy(vmpool, vmh):
    """ Destroy a single resource. """

    vm_name = vmh.name
    logging.debug("%s removing resource %s", vmh.profile.name, vm_name)

    vm_state = vmpool.state_get(vm_name)
    if vm_state != testpool.core.api.Pool.STATE_NONE:
        vmpool.destroy(vm_name)

    if vmh.profile.resource_set.all().count() > vmh.profile.vm_max:
        try:
            vmh.delete()
        except models.Resource.DoesNotExist:
            pass
