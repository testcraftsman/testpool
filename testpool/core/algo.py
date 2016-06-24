"""
   Algorithm for modifying database.
"""
import sys
import logging
import traceback
from testpooldb import models
import testpool.core.api


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


def setup(ext, profile):
    """ Setup hypervisor. """

    logging.info("algo.setup %s %s", profile.name, profile.template_name)

    vmpool = ext.vmpool_get(profile.hv.hostname)

    logging.info("setup HV %s", profile.hv)

    for count in range(profile.vm_max):
        vm_name = profile.template_name + ".%d" % count
        (vm1, gcr) = models.VM.objects.get_or_create(profile=profile,
                                                     name=vm_name)
        vm_state = vmpool.vm_state_get(vm_name)
        logging.debug("setup %s VM %s state %d", profile.name, vm1, vm_state)
        if vm_state != testpool.core.api.VMPool.STATE_NONE:
            vmpool.destroy(vm_name)

        vmpool.clone(profile.template_name, vm_name)
        vm_state = vmpool.start(vm_name)
        vm_state_str = testpool.core.api.VMPool.STATE_STRING[vm_state]
        logging.debug("setup %s VM cloned %s %s", profile.name, vm1,
                      vm_state_str)
        if vm_state != testpool.core.api.VMPool.STATE_RUNNING:
            logging.error("setup %s VM %s failed to start", profile.name, vm1)
            (kvp, _) = models.KVP.get_or_create("state", "bad")
            vm1.profile.kvp_get_or_create(kvp)
            vm1.status = models.VM.RELEASED
        else:
            (kvp, _) = models.KVP.get_or_create("state", "bad")
            vm1.profile.kvp_get_or_create(kvp)
            vm1.status = models.VM.FREE
            logging.info("%s: vm %s is available", profile.name, vm1.name)
        vm1.save()

    return 0


def pop(ext, profile_name):
    """ Pop one VM from the VMPool. """

    logging.info("algo.pop VM from %s", profile_name)
    vmpool = ext.vmpool_get(profile.hv.name)

    profile1 = models.Profile.objects.get(name=profile_name)

    try:
        vm1 = models.VM.objects.filter(profile=profile1,
                                       status=models.VM.FREE)[0]
        vm1.status = models.VM.RESERVED
        vm1.save()
        vmpool.pop(profile_name, vm1.name)
    except Exception:
        raise NoResources("%s: all VMs taken" % profile_name)

    return vm1


def push(ext, vm_id):
    """ Push one VM by id. """

    logging.info("push %d", vm_id)

    vmpool = ext.vmpool_get(profile.hv.hostname)

    try:
        vm1 = models.VM.objects.get(id=vm_id, status=models.VM.RESERVED)
        vm1.status = models.VM.RELEASED
        vm1.save()
        vmpool.push(vm1.profile.name, vm1.name)

        return 0
    except models.VM.DoesNotExist:
        raise ResourceReleased(vm_id)


def reclaim(ext, vmh):
    """ Reclaim a VM and rebuild it. """

    logging.debug("reclaiming %s", vmh.name)

    vmpool = ext.vmpool_get(vmh.profile.hv.hostname)

    vmpool.destroy(vmh.name)
    vmpool.clone(vmh.profile.template_name, vmh.name)
