"""
Examples on how to call the Testpool REST interfaces. Read the quick start
guide in order to configure Testpoo..

Make sure VMs are avaliable, run:

  ./bin/tpl profile list

Check to see that 3/3 for VMs. This is only necessary because of the
global example of vm_hndl.

The database needs to be running in order for these examples can run. To run
the database from the git clone:

  ./bin/tpl-db runserver

To run this file type

  py.test -s examples/python_api.py

These examples illustrates the use of the testpool.client. The global variable
RESOURCE acquires a single VM which stays acquired until this testsuite ends.
Once a VM is acquired, this test can login and use the VM throughout the
entire testsuite.

This example checks for a hypervisor profile named example . If
one does not exist, then a fake profile is created.  A fake.profile is used
to show examples without having to take the time to configure an actual
hypervisor.

If you want to use an actual hypervisor, create a working VM called
test.template and shut it down. This is the template cloned in this
example as test.template.0
"""
import time
import unittest
import testpool.client
import conftest


class Testsuite(unittest.TestCase):
    """ Demonstrate testpool.client API. """

    def test_vm_acquire(self):
        """ test_vm_acquire.

        Use the global RESOURCE. Acquiring a VM means that this VM can be
        used.
        """
        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10, True)
        current_vms = hndl.detail_get()["vm_avaliable"]
        hndl.acquire()
        ##
        # The ip attribute provides the IP address of the VM.
        self.assertTrue(hndl.ip_addr is not None)
        details = hndl.detail_get()
        self.assertTrue(details["vm_avaliable"] < current_vms)
        hndl.release()
        for _ in range(10 * 5):
            time.sleep(6)
            details = hndl.detail_get()
            self.assertTrue(details)
            if details["vm_avaliable"] == current_vms:
                return
        details = hndl.detail_get()
        self.assertTrue(details)
        self.assertEqual(details["vm_avaliable"], current_vms)

    def test_vm_context_manager(self):
        """ show an example of the client contact manager. """

        ##
        # Shows an example of the context manager.
        with testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                    conftest.GLOBAL["profile"], 10) as hndl:
            ##
            # This assert is to show that a different VM was picked.
            self.assertTrue(hndl.vm.id is not None)
            self.assertTrue(hndl.vm.ip_addr is not None)

    def test_detail_get(self):
        """ show an example of the client contact manager. """

        ##
        # Shows an example of the context manager.
        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10)
        details = hndl.detail_get()
        self.assertTrue(details)
        self.assertEqual(details["vm_max"], 3)

    def test_blocking(self):
        """ test_blocking. show waiting for VM to be avaliable.

        There are at most 3 VMs available so take 4. With blocking
        there should never be an exception thrown.
        """

        ip_addresses = set()
        ##
        # Shows an example of the context manager.
        for count in range(3):
            with testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                        conftest.GLOBAL["profile"],
                                        10, True) as hndl:
                ##
                # This assert is to show that a different VM was picked.
                self.assertTrue(hndl.vm)
                ip_addresses.add(hndl.vm.ip_addr)

        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10, True)
        hndl.acquire(True)
        self.assertTrue(hndl.vm.ip_addr not in ip_addresses)
        hndl.release()

        count = 0
        for _ in range(100):
            details = hndl.detail_get()
            count = details["vm_avaliable"]
            if count == 3:
                return
            time.sleep(20)
        raise ValueError("never recovered all three VMs.")
