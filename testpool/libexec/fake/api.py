"""
API for KVM hypervisors.
"""
import os
import logging
import unittest
from contextlib import contextmanager
import yaml
import testpool.core.api


__STORE_PATH__ = "/tmp/testpool/memory"


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

    yield vms

    ##
    # Now store the vms content into the file.
    with open(store_path, "w") as stream:
        stream.write(yaml.dump(vms, default_flow_style=True))


class VMPool(testpool.core.api.VMPool):
    """ Interface to KVM Pool manager. """

    def __init__(self, context):
        """ Constructor. """
        testpool.core.api.VMPool.__init__(self, context)

    def type_get(self):
        """ Return the type of the interface. """
        return "memory"

    def destroy(self, vm_name):
        """ Destroy VM. """

        logging.debug("memory destroy %s", vm_name)
        with db_ctx(self.context) as vms:
            vms.remove(vm_name)
        return 0

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        logging.debug("memory clone %s %s", orig_name, new_name)
        with db_ctx(self.context) as vms:
            vms.add(orig_name)
            vms.add(new_name)

        return 0

    def start(self, vm_name):
        """ Start VM. """

        with db_ctx(self.context) as vms:
            if vm_name in vms:
                return testpool.core.api.VMPool.STATE_RUNNING
            else:
                return testpool.core.api.VMPool.STATE_BAD_STATE

    def vm_state_get(self, vm_name):
        """ Start VM. """

        with db_ctx(self.context) as vms:
            if vm_name in vms:
                return testpool.core.api.VMPool.STATE_RUNNING
            else:
                return testpool.core.api.VMPool.STATE_NONE


def vmpool_get(url_name):
    """ Return a handle to the KVM API. """
    return VMPool(url_name)


class Testsuite(unittest.TestCase):
    """ Test api. """
    def test_db_ctx(self):
        """ test_db_ctx. """
        store_path = "/tmp/testpool/memory"
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
