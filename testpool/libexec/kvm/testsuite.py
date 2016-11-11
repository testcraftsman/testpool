"""
Tests KVM API

Change the TEST_HOST global variable to your hypervisor and create a
test.template VM.
"""
import time
import unittest
import logging
import libvirt
from testpooldb import models
from testpool.libexec import kvm
from testpool.core import server
from testpool.core import ext
from testpool.core import algo

TEST_HOST = "192.168.0.222"
TEST_PROFILE = "test.kvm.profile"
TEST_TEMPLATE = "test.template"


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def setUp(self):
        """ Create KVM profile. """

        (hv1, _) = models.HV.objects.get_or_create(hostname=TEST_HOST,
                                                   product="kvm")
        models.Profile.objects.get_or_create(name=TEST_PROFILE, hv=hv1,
                                             template_name=TEST_TEMPLATE,
                                             vm_max=3)

    def tearDown(self):
        """ Remove any previous test profiles1. """

        try:
            profile1 = models.Profile.objects.get(name=TEST_PROFILE)
            for vm1 in models.VM.objects.filter(profile=profile1):
                vm1.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            hv1 = models.HV.objects.get(hostname=TEST_HOST, product="kvm")
            hv1.delete()
        except models.HV.DoesNotExist:
            pass

    def test_clone(self):
        """ test clone.
        Clone three VMs. """

        fmt = "qemu+ssh://testpool@%s/system"
        url = fmt % TEST_HOST
        hv1 = libvirt.open(url)
        self.assertTrue(hv1)

        vmpool = kvm.api.VMPool(url, "test")
        self.assertTrue(vmpool)
        for item in range(3):
            vm_name = TEST_TEMPLATE + ".%d" % item
            try:
                vmpool.destroy(vm_name)
            except libvirt.libvirtError:
                continue

        pool = [item for item in vmpool.conn.listAllDomains()]
        pool = [item.name() for item in pool]
        pool = [item for item in pool if item.startswith(TEST_TEMPLATE)]
        for item in range(3):
            vm_name = TEST_TEMPLATE + ".%d" % item
            if vm_name not in pool:
                logging.debug("creating %s", vm_name)
                vmpool.clone(TEST_TEMPLATE, vm_name)
                vmpool.start(vm_name)

        for item in range(3):
            vm_name = "test.template.%d" % item
            try:
                vmpool.destroy(vm_name)
            except libvirt.libvirtError:
                continue

    def test_info(self):
        """ test_info """

        fmt = "qemu+ssh://testpool@%s/system"
        cmd = fmt % TEST_HOST

        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)

        self.assertTrue(hndl.getInfo())
        self.assertTrue(hndl.getHostname())

    def test_storage(self):
        """ test_storage """
        fmt = "qemu+ssh://testpool@%s/system"
        cmd = fmt % TEST_HOST
        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)
        for item in hndl.listDefinedDomains():
            print "VM: defined", item

        for item in hndl.listDomainsID():
            dom = hndl.lookupByID(item)
            print "Active: Name: ", dom.name()
            print "Active: Info: ", dom.info()

    def test_destroy_missing(self):
        """ test_destroy_missing. """

        profile1 = models.Profile.objects.get(name=TEST_PROFILE)

        fmt = "qemu+ssh://testpool@%s/system"
        connect = fmt % TEST_HOST
        hv1 = kvm.api.vmpool_get(profile1)
        self.assertTrue(hv1)

        hndl = libvirt.open(connect)
        self.assertTrue(hndl)

        try:
            vm_name = "test.template.destroy"
            hv1.start(vm_name)
        except libvirt.libvirtError:
            pass


# pylint: disable=R0903
class FakeArgs(object):
    """ Used in testing to pass values to server.main. """
    def __init__(self):
        self.count = 30
        self.sleep_time = 0
        self.max_sleep_time = 0
        self.min_sleep_time = 0
        self.setup = True


class TestsuiteServer(unittest.TestCase):
    """ Test model output. """

    def test_setup(self):
        """ test_setup. """

        # fmt = "qemu+ssh://testpool@%s/system"
        (hv1, _) = models.HV.objects.get_or_create(hostname=TEST_HOST,
                                                   product="kvm")

        defaults = {"vm_max": 1, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="test.kvm.profile", hv=hv1, defaults=defaults)

        args = FakeArgs()
        self.assertEqual(server.main(args), 0)
        profile1.delete()

    def test_shrink(self):
        """ test_shrinkg. test when the profile shrinks. """

        product = "kvm"
        hostname = TEST_HOST

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": 10, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="test.kvm.profile", hv=hv1, defaults=defaults)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()
        ##

        args = FakeArgs()
        self.assertEqual(server.main(args), 0)
        exts = ext.api_ext_list()

        vmpool = exts[product].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list()), 2)

    def test_expand(self):
        """ test_expand. """

        product = "kvm"
        hostname = "localhost"
        profile_name = "test.server.profile"

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": 3, "template_name": "kvm.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=profile_name, hv=hv1, defaults=defaults)

        ##
        # Now expand to 12
        profile1.vm_max = 12
        profile1.save()
        ##

        args = FakeArgs()
        self.assertEqual(server.main(args), 0)

        exts = ext.api_ext_list()
        vmpool = exts[product].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list()), 12)

    def test_expiration(self):
        """ test_expiration. """

        product = "fake"
        hostname = "localhost"
        profile_name = "test.server.profile"
        vm_max = 3

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": vm_max, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=profile_name, hv=hv1, defaults=defaults)

        args = FakeArgs()
        self.assertEqual(server.main(args), 0)

        vms = profile1.vm_set.filter(status=models.VM.READY)
        self.assertEqual(len(vms), vm_max)

        vmh = vms[0]

        ##
        # Acquire for 3 seconds.
        vmh.transition(models.VM.RESERVED, algo.ACTION_DESTROY, 3)
        time.sleep(5)
        # LOGGER.setLevel(logging.DEBUG)
        args.setup = False
        args.count = 2
        args.sleep_time = 1
        args.max_sleep_time = 1
        args.min_sleep_time = 1
        self.assertEqual(server.main(args), 0)
        ##

        exts = ext.api_ext_list()
        server.adapt(exts)

        vms = profile1.vm_set.filter(status=models.VM.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(vms.count(), 2)
        ##

if __name__ == "__main__":
    unittest.main()
