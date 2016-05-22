"""
API for KVM hypervisors.
"""

import logging
from xml.etree import ElementTree
import libvirt
import virtinst.CloneManager as clmgr
import testpool.core.api
from virtinst.User import User


class VMPool(testpool.core.api.VMPool):
    """ Interface to KVM Pool manager. """

    def __init__(self, context):
        """ Constructor. """
        VMPool.__init__(self, context)

        self.vms = set()

    def type_get(self):
        """ Return the type of the interface. """
        return "memory"

    def destroy(self, vm_name):
        """ Destroy VM. """
        logging.debug("memory destroy %s", vm_name)
        self.vms.remove(vm_name)

        return 0

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        logging.debug("memory clone %s %s", orig_name, new_name)
        self.vms.add(orig_name)
        self.vms.add(new_name)

        return 0

    def start(self, vm_name):
        """ Start VM. """

        if vm_name in self.vms:
            return testpool.core.api.VMPool.STATE_RUNNING
        else:
            return testpool.core.api.VMPool.STATE_BAD_STATE

    def vm_state_get(self, vm_name):
        """ Start VM. """

        if vm_name in self.vms:
            return testpool.core.api.VMPool.STATE_RUNNING
        else:
            return testpool.core.api.VMPool.STATE_NONE

    def profile_mark_bad(self, profile_name):
        raise ValueError("profile %s should never fail", profile_name)


def vmpool_get(url_name):
    """ Return a handle to the KVM API. """

    return VMPool(url_name)
