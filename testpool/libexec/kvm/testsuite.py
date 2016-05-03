"""
Tests KVM API
"""
import unittest
import logging
import libvirt
from testpool.libexec import kvm

TEST_HOST = "192.168.0.27"


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def test_clone(self):
        """ test clone """

        fmt = "qemu+ssh://mhamilton@%s/system"
        connect = fmt % TEST_HOST
        hv1 = kvm.api.vmpool_get(connect)
        self.assertTrue(hv1)

        hndl = libvirt.open(connect)
        self.assertTrue(hndl)

        for item in range(3):
            vm_name = "pool.ubuntu1404.%d" % item
            try:
                hv1.destroy(vm_name)
            except libvirt.libvirtError:
                continue

        pool = [item for item in hv1.conn.listAllDomains()]
        pool = [item.name() for item in pool]
        pool = [item for item in pool if item.startswith("pool.ubuntu1404")]
        for item in range(3):
            vm_name = "pool.ubuntu1404.%d" % item
            if vm_name not in pool:
                logging.debug("creating %s", vm_name)
                hv1.clone("template.ubuntu1404", vm_name)
                hv1.start(vm_name)

        for item in range(3):
            vm_name = "pool.ubuntu1404.%d" % item
            try:
                hv1.destroy(vm_name)
            except libvirt.libvirtError:
                continue

    def test_info(self):
        """ test_info """

        fmt = "qemu+ssh://mhamilton@%s/system"
        cmd = fmt % TEST_HOST
        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)

        self.assertTrue(hndl.getInfo())
        self.assertTrue(hndl.getHostname())

    def test_storage(self):
        """ test_storage """
        fmt = "qemu+ssh://mhamilton@%s/system"
        cmd = fmt % TEST_HOST
        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)
        for item in hndl.listDefinedDomains():
            print "VM: defined", item

        for item in hndl.listDomainsID():
            dom = hndl.lookupByID(item)
            print "Active: Name: ", dom.name()
            print "Active: Info: ", dom.info()

    def test_destroy(self):
        """ test_destroy. """

        fmt = "qemu+ssh://mhamilton@%s/system"
        connect = fmt % TEST_HOST
        hv1 = kvm.api.vmpool_get(connect)
        self.assertTrue(hv1)

        hndl = libvirt.open(connect)
        self.assertTrue(hndl)

        try:
            vm_name = "pool.ubuntu1404.destroy"
            hv1.clone("template.ubuntu1404", vm_name)
            hv1.start(vm_name)
        except ValueError:
            pass

        hv1.destroy(vm_name)

    def test_create_idempotent(self):
        """ test_create_idempotent. """

        fmt = "qemu+ssh://mhamilton@%s/system"
        connect = fmt % TEST_HOST
        hv1 = kvm.api.vmpool_get(connect)

        hndl = libvirt.open(connect)
        self.assertTrue(hndl)

        vm_name = "pool.ubuntu1404.create"
        try:
            logging.info("%s: cloning", vm_name)
            hv1.clone("template.ubuntu1404", vm_name)
            hv1.start(vm_name)
        except ValueError:
            pass

        try:
            logging.info("%s: cloning", vm_name)
            hv1.clone("template.ubuntu1404", vm_name)
            hv1.start(vm_name)
        except ValueError:
            pass

        hv1.destroy(vm_name)

        try:
            hv1.clone("template.ubuntu1404", vm_name)
            hv1.start(vm_name)
        except ValueError:
            pass

        hv1.destroy(vm_name)

    def test_create_destroy(self):
        """ test_create_destroy. """

        fmt = "qemu+ssh://mhamilton@%s/system"
        connect = fmt % TEST_HOST
        hv1 = kvm.api.vmpool_get(connect)

        hndl = libvirt.open(connect)
        self.assertTrue(hndl)

        vm_name = "pool.ubuntu1404.create_destroy"
        for _ in range(5):
            try:
                logging.info("%s: cloning", vm_name)
                hv1.clone("template.ubuntu1404", vm_name)
                hv1.start(vm_name)
            except ValueError:
                pass

            hv1.destroy(vm_name)

if __name__ == "__main__":
    unittest.main()
