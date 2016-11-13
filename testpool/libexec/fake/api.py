"""
API for KVM hypervisors.
"""
import os
import logging
import unittest
from contextlib import contextmanager
import yaml
import testpool.core.api


__STORE_PATH__ = "/tmp/testpool/fake"


def db_vm_read(context):
    """ Read the current database of VMS. """

    store_path = os.path.join(__STORE_PATH__, context)
    if os.path.exists(store_path):
        vms = set()
        with open(store_path, "r") as stream:
            try:
                vms = yaml.safe_load(stream)
                if not vms:
                    vms = set()
            except yaml.YAMLError:
                vms = set()
    else:
        vms = set()

    return vms


@contextmanager
def db_ctx(context):
    """ Return VM list. """

    store_path = __STORE_PATH__

    try:
        os.makedirs(store_path)
    except OSError:
        pass

    store_path = os.path.join(store_path, context)

    ##
    # Check to see if the context creates a sub directory.
    (store_dir, _) = os.path.split(store_path)

    try:
        os.makedirs(store_dir)
    except OSError:
        pass
    ##
    vms = db_vm_read(context)

    yield vms

    ##
    # Now store the vms content into the file.
    with open(store_path, "w") as stream:
        stream.write(yaml.dump(vms, default_flow_style=True))
    ##


class VMPool(testpool.core.api.VMPool):
    """ Interface to KVM Pool manager. """

    def __init__(self, context):
        """ Constructor. """
        testpool.core.api.VMPool.__init__(self, context)

    def timing_get(self, request):
        """ Return algorithm timing based on the request. """

        if request == testpool.core.api.VMPool.TIMING_REQUEST_DESTROY:
            return 1
        else:
            raise ValueError("unknown timing request %s", request)

    def type_get(self):
        """ Return the type of the interface. """
        return "fake"

    def destroy(self, vm_name):
        """ Destroy VM. """

        vm_name = str(vm_name)

        logging.debug("fake destroy %s", vm_name)
        with db_ctx(self.context) as vms:
            if vm_name in vms:
                vms.remove(vm_name)
        return 0

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        orig_name = str(orig_name)
        new_name = str(new_name)

        logging.debug("fake clone %s %s", orig_name, new_name)
        with db_ctx(self.context) as vms:
            vms.add(new_name)

        return 0

    def start(self, vm_name):
        """ Start VM. """
        logging.debug("fake start %s", vm_name)

        with db_ctx(self.context) as vms:
            if vm_name in vms:
                return testpool.core.api.VMPool.STATE_RUNNING
            else:
                return testpool.core.api.VMPool.STATE_BAD_STATE

    def vm_state_get(self, vm_name):
        """ Start VM. """
        logging.debug("fake vm_state_get %s", vm_name)

        with db_ctx(self.context) as vms:
            if vm_name in vms:
                return testpool.core.api.VMPool.STATE_RUNNING
            else:
                return testpool.core.api.VMPool.STATE_NONE

    def vm_list(self, profile1):
        """ Start VM. """

        logging.debug("fake vm_list")

        result = list(db_vm_read(self.context))

        result = [item for item in result if self.vm_is_clone(profile1, item)]

        return result

    # pylint: disable=W0613
    # pylint: disable=R0201
    def ip_get(self, vm_name):
        """ Return VM IP address used to connect to the VM.
        @param vm_name Return the IP off the vm_name.
        """

        return "127.0.0.1"

    # pylint: disable=W0613
    # pylint: disable=R0201
    def vm_attr_get(self, vm_name):
        """ Return the list of attributes for the VM.

        These attributes are stored in the database, eventually they are
        passed through the REST interface to the client.
        """

        return {"ip": "127.0.0.1"}

    def vm_is_clone(self, profile1, vm_name):
        """ Return True if vm1 is a clone of profile1 template. """

        return vm_name.startswith(profile1.template_name)


def vmpool_get(profile1):
    """ Return a handle to the KVM API. """

    context = "%s/%s" % (profile1.hv.hostname, profile1.name)
    return VMPool(context)


class Testsuite(unittest.TestCase):
    """ Test api. """
    def test_db_ctx(self):
        """ test_db_ctx. """
        store_path = "/tmp/testpool/fake"
        context = "testsuite/test_db_ctx"

        with db_ctx(context) as vms:
            vms.add("vm1")
            vms.add("vm2")

        with db_ctx(context) as vms:
            self.assertTrue("vm1" in vms)
            self.assertTrue("vm2" in vms)
            self.assertEqual(len(vms), 2)

        store_path = os.path.join(store_path, context)
        self.assertTrue(os.path.exists(store_path))

if __name__ == "__main__":
    unittest.main()
