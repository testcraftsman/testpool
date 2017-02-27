"""
Examples on how to call the Testpool REST interfaces. Read the quick start
guide in order to configure Testpool and then come back to this script.

As discussed in the quickstart guide. This example uses a Testpool profile
named example. These examples work best when all VMs have been cloned
and have retrieved their IP address.  Make sure VMs are avaliable, run:

  ./bin/tpl profile list

To run this file type

  py.test -s examples/python_api.py

These examples illustrates the use of the testpool.client. The global variable
GLOBAL in conftest defines the Testpool profile. Once a VM is acquired, this
test can login and use the VM throughout the entire testsuite. This assumes
that the VM has negotiated an IP address usually throught DHCP.

This example checks for a hypervisor profile named example. If
one does not exist, a fake profile is created.  A fake.profile is used
to show examples without having to take the time to configure an actual
hypervisor.

As these examples are running, use virt-manager to see the hypervisor change.
"""
import time
import unittest
import testpool.client
import conftest


class Testsuite(unittest.TestCase):
    """ Demonstrate testpool.client API. """

    def test_vm_acquire(self):
        """ test_vm_acquire.

        Acquire a single VM. Demonstrate how to determine the VMs IP address.
        """
        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10, True)
        current_vms = hndl.detail_get()["vm_available"]
        hndl.acquire()
        ##
        # The ip attribute provides the IP address of the VM.
        self.assertTrue(hndl.ip_addr is not None)
        ##

        ##
        # Assert that one VM was acquires. The number of avaliable VMs
        # will now be less max.
        details = hndl.detail_get()
        self.assertTrue(details["vm_available"] < current_vms)
        hndl.release()
        for _ in range(40 * 6):
            time.sleep(5)
            details = hndl.detail_get()
            self.assertTrue(details)
            if details["vm_available"] == current_vms:
                return
        details = hndl.detail_get()
        self.assertTrue(details)
        self.assertEqual(details["vm_available"], current_vms)

    def test_vm_context_manager(self):
        """ show using client context manager. """

        ##
        # Shows an example of the context manager.
        with testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                    conftest.GLOBAL["profile"], 10) as hndl:
            ##
            # This assert is to show that a different VM was picked.
            self.assertTrue(hndl.vm.id is not None)
            self.assertTrue(hndl.vm.ip_addr is not None)
            ##
        ##

    def test_detail_get(self):
        """ Show Hypervisor details. """

        ##
        # Shows an example of the context manager.
        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10)
        details = hndl.detail_get()
        self.assertTrue(details)
        self.assertEqual(details["vm_max"], 3)
        ##

    def test_blocking(self):
        """ test_blocking. show waiting for VM to be available.

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
                ##
        ##

        hndl = testpool.client.VMHndl(conftest.GLOBAL["hostname"],
                                      conftest.GLOBAL["profile"], 10, True)
        hndl.acquire(True)
        self.assertTrue(hndl.vm.ip_addr not in ip_addresses)
        hndl.release()

        count = 0
        for _ in range(100):
            details = hndl.detail_get()
            count = details["vm_available"]
            if count == 3:
                return
            time.sleep(20)
        raise ValueError("never recovered all three VMs.")
