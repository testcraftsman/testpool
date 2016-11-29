"""
Examples on how to call the REST interfaces.

To run this file type

  py.test -s examples/python_api.py

These examples illustrates the use of the testpool.client.  The database needs
to be running in order for these examples can run. To run the
database from the git clone:

  ./bin/tpl-db runserver

The global variable RESOURCE acquires a single VM which stays acquired until
this testsuite ends.  Once a VM is acquired, this test can login and use the
VM throughout the entire testsuite.


This example checks for a hypervisor profile named test.profile. If
one does not exist, then a fake profile is created.  A fake.profile is used
to show examples without having to take the time to configure an actual
hypervisor.

If you want to use an actual hypervisor, create a working VM called
test.template and shut it down. This is the template cloned in this
example as test.template.0
"""
import unittest
import pytest
import testpool.client
import conftest


GLOBAL = {"resource": None}


@pytest.yield_fixture(scope="module", autouse=True)
def vm_hndl():
    """ provide an example of a global RESOURCE for the entire test."""

    with testpool.client.VMHndl(conftest.GLOBAL["hypervisor"],
                                "test.profile") as hndl:
        GLOBAL["resource"] = hndl
        yield hndl


class Testsuite(unittest.TestCase):
    """ Demonstrate testpool.client API. """

    def test_vm_global_acquire(self):
        """ test_vm_acquire.

        Use the global RESOURCE. Acquiring a VM means that this VM can be
        used.
        """

        ##
        # The ip attribute provides the IP address of the VM. The testsuite
        # uses a fake profile where all VMs use 127.0.0.1.
        self.assertEqual(GLOBAL["resource"].ip_addr,
                         conftest.GLOBAL["hypervisor"])

    def test_vm_context_manager(self):
        """ show an example of the client contact manager. """

        ##
        # Shows an example of the context manager.
        with testpool.client.VMHndl(conftest.GLOBAL["hypervisor"],
                                    "test.profile") as hndl:
            ##
            # This assert is to show that a different VM was picked.
            # Normally vm.ip will point to another VM, but for the test.profile
            # all VMs have 127.0.0.1 IP address.
            self.assertNotEqual(hndl.vm.id, GLOBAL["resource"].vm.id)
