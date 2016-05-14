"""
API for KVM hypervisors.
"""
import logging
from xml.etree import ElementTree
import libvirt
import virtinst.CloneManager as clmgr
from virtinst.User import User


class VMPool(object):
    """ Interface to KVM Pool manager. """
    def __init__(self, name):
        """ Constructor. """
        self.name = name

    def type_get(self):
        """ Return the type of the interface. """
        return "memory"

    def destroy(self, vm_name):
        """ Destroy VM. """
        logging.debug("memory destroy %s", vm_name)

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        logging.debug("memory clone %s %s", orig_name, new_name)

    def start(self, vm_name):
        """ Start VM. """

        vm_dom = self.conn.lookupByName(vm_name)
        vm_dom.create()


def vmpool_get(url_name):
    """ Return a handle to the KVM API. """

    return VMPool(url_name)
