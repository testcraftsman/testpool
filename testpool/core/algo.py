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


def adapt(vmpool, profile):
    """ Adapt the pool to the profile size.
    @return Returns the number of changes. Positive number indicates the
            number of VMs created.
    """

    changes = 0

    vm_list = vmpool.vm_list()

    ##
    # Now remove any extract VMs because the maximum VMs was reduced.
    # The first number used is 0.
    vm_current = len(vm_list)

    ##
    if vm_current == profile.vm_max:
        return changes
    elif vm_current > profile.vm_max:
        for vm_number in range(profile.vm_max, vm_current+1):
            changes -= 1
            vm_name = profile.template_name + ".%d" % vm_number
            logging.debug("setup %s reducing pool %s destroyed", profile.name,
                          vm_name)
            vmpool.destroy(vm_name)

            try:
                vm1 = models.VM.objects.get(profile=profile, name=vm_name)
                vm1.delete()
            except models.VM.DoesNotExist:
                pass
    else:
        ##
        # there are not enough VMs. Add more.
        for count in range(profile.vm_max):
            changes += 1
            vm_name = profile.template_name + ".%d" % count
            (vm1, _) = models.VM.objects.get_or_create(profile=profile,
                                                       name=vm_name)
            vm_state = vmpool.vm_state_get(vm_name)
            if vm_state == testpool.core.api.VMPool.STATE_NONE:
                logging.debug("%s expanding pool VM with %s ", profile.name,
                              vm_name)
                vmpool.clone(profile.template_name, vm_name)
                vm_state = vmpool.start(vm_name)

                if vm_state != testpool.core.api.VMPool.STATE_RUNNING:
                    logging.error("%s VM clone %s failed", profile.name,
                                  vm_name)
                    (kvp, _) = models.KVP.get_or_create("state", "bad")
                    vm1.profile.kvp_get_or_create(kvp)
                    vm1.status = models.VM.RELEASED
                else:
                    logging.debug("%s VM cloned %s", profile.name, vm_name)
                    (kvp, _) = models.KVP.get_or_create("state", "bad")
                    vm1.profile.kvp_get_or_create(kvp)
                    vm1.status = models.VM.FREE
            vm1.save()
        ##
    return changes


def remove(vmpool, profile):
    """ Remove all VMs from the host. """

    for count in range(profile.vm_max):
        vm_name = profile.template_name + ".%d" % count
        try:
            vm1 = models.VM.objects.get(profile=profile, name=vm_name)
            vm1.delete()
        except models.VM.DoesNotExist:
            pass

        vm_state = vmpool.vm_state_get(vm_name)
        if vm_state != testpool.core.api.VMPool.STATE_NONE:
            logging.debug("%s removing VM %s", profile.name, vm_name)
            vmpool.destroy(vm_name)


def pop(hostname, product, profile_name):
    """ Pop one VM from the VMPool. """

    logging.info("algo.pop VM from %s", profile_name)

    hv1 = models.HV.objects.get(hostname=hostname, product=product)
    profile1 = models.Profile.objects.get(hv=hv1, name=profile_name)

    vms = models.VM.objects.filter(profile=profile1, status=models.VM.FREE)
    if vms.count() == 0:
        raise NoResources("%s: all VMs taken" % profile_name)

    vm1 = vms[0]
    vm1.status = models.VM.RESERVED
    vm1.save()

    return vm1


def push(vm_id):
    """ Push one VM by id. """

    logging.info("push %d", vm_id)
    try:
        vm1 = models.VM.objects.get(id=vm_id, status=models.VM.RESERVED)
        vm1.status = models.VM.RELEASED
        vm1.save()
        return 0
    except models.VM.DoesNotExist:
        raise ResourceReleased(vm_id)


def reclaim(vmpool, vmh):
    """ Reclaim a VM and rebuild it. """

    logging.debug("reclaiming %s", vmh.name)

    vmpool.destroy(vmh.name)
    vmpool.clone(vmh.profile.template_name, vmh.name)
    vmpool.start(vmh.name)
