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
    """ Read the current database of resources. """

    store_path = os.path.join(__STORE_PATH__, context)
    if os.path.exists(store_path):
        rsrcs = set()
        with open(store_path, "r") as stream:
            try:
                rsrcs = yaml.safe_load(stream)
                if not rsrcs:
                    rsrcs = set()
            except yaml.YAMLError:
                rsrcs = set()
    else:
        rsrcs = set()

    return rsrcs


@contextmanager
def db_ctx(context):
    """ Return resource list. """

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
    rsrcs = db_vm_read(context)

    yield rsrcs

    ##
    # Now store the rsrcs content into the file.
    with open(store_path, "w") as stream:
        stream.write(yaml.dump(rsrcs, default_flow_style=True))
    ##


# pylint: disable=R0902
# pylint: disable=R0903
class HostInfo(testpool.core.api.HostInfo):
    """ Host info. """

    def __init__(self):
        testpool.core.api.HostInfo.__init__(self)
        self.model = None
        self.memory_size = 0
        self.cpus = 0
        self.cpu_mhz = 0
        self.numa_nodes = 0
        self.cpu_sockets = 0
        self.cores_per_socket = 0
        self.threads_per_core = 0


class Pool(testpool.core.api.Pool):
    """ Interface to KVM Pool manager. """

    def __init__(self, context):
        """ Constructor. """
        testpool.core.api.Pool.__init__(self, context)

    def new_name_get(self, template_name, index):
        """ Given a profile, generate a new name. """

        name = template_name + ".%d" % index
        return name

    def timing_get(self, request):
        """ Return algorithm timing based on the request.
        :return time (sec) Return the amount of time to wait in seconds. """

        if request == testpool.core.api.Pool.TIMING_REQUEST_DESTROY:
            return 1
        else:
            raise ValueError("unknown timing request %s" % request)

    def type_get(self):
        """ Return the type of the interface. """
        return "fake"

    def destroy(self, name):
        """ Destroy resource. """

        name = str(name)

        logging.debug("fake destroy %s", name)
        with db_ctx(self.context) as rsrcs:
            if name in rsrcs:
                rsrcs.remove(name)
        return 0

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        orig_name = str(orig_name)
        new_name = str(new_name)

        logging.debug("fake clone %s %s", orig_name, new_name)
        with db_ctx(self.context) as rsrcs:
            rsrcs.add(new_name)

        return 0

    def start(self, name):
        """ Start resource. """
        logging.debug("fake start %s", name)

        with db_ctx(self.context) as rsrcs:
            if name in rsrcs:
                return testpool.core.api.Pool.STATE_RUNNING
            return testpool.core.api.Pool.STATE_BAD_STATE

    def state_get(self, name):
        """ Return the state of a resource. """
        logging.debug("fake state_get %s", name)

        with db_ctx(self.context) as rsrcs:
            if name in rsrcs:
                return testpool.core.api.Pool.STATE_RUNNING
            return testpool.core.api.Pool.STATE_NONE

    def list(self, profile1):
        """ Start resource. """

        logging.debug("fake list")

        result = list(db_vm_read(self.context))

        result = [item for item in result if self.is_clone(profile1, item)]

        return result

    # pylint: disable=W0613
    # pylint: disable=R0201
    def ip_get(self, name):
        """ Return resource IP address used to connect to the resource.

        @param name Return the IP off the name.
        """
        return "127.0.0.1"

    # pylint: disable=W0613
    # pylint: disable=R0201
    def resource_attr_get(self, name):
        """ Return the list of attributes for the resource.

        These attributes are stored in the database, eventually they are
        passed through the REST interface to the client.
        """

        return {"ip": "127.0.0.1"}

    def is_clone(self, profile1, name):
        """ Return True if vm1 is a clone of profile1 template. """

        return (name.startswith(profile1.template_name) and
                name != profile1.template_name)

    def info_get(self):
        """ Return information about the hypervisor profile. """

        ret_value = HostInfo()
        return ret_value


def pool_get(profile1):
    """ Return a handle to the KVM API. """

    context = "%s/%s" % (profile1.hv.connection, profile1.name)
    return Pool(context)


class Testsuite(unittest.TestCase):
    """ Test api. """
    def test_db_ctx(self):
        """ test_db_ctx. """
        store_path = "/tmp/testpool/fake"
        context = "testsuite/test_db_ctx"

        with db_ctx(context) as rsrcs:
            rsrcs.add("rsrc1")
            rsrcs.add("rsrc2")

        with db_ctx(context) as rsrcs:
            self.assertTrue("rsrc1" in rsrcs)
            self.assertTrue("rsrc2" in rsrcs)
            self.assertEqual(len(rsrcs), 2)

        store_path = os.path.join(store_path, context)
        self.assertTrue(os.path.exists(store_path))


if __name__ == "__main__":
    unittest.main()
