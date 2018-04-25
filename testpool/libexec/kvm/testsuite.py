# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testpool
#
# Testbed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Testbed is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Testdb.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests KVM API

In order to run these tests, either:
  - change the TEST_HOST global variable to your hypervisor and create
    a test.template resource.
  - Use existing CONNECTION and use a localhost KVM hypvervisor and
    create a test.template resource.
Also, make sure tpl-daemon is NOT running.
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

CONNECTION = "qemu:///system"
TEST_PROFILE = "test.kvm.profile"
TEMPLATE = "test.template"
PRODUCT = "kvm"


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a resource. """

    def setUp(self):
        """ Create KVM profile. """

        (hv1, _) = models.HV.objects.get_or_create(
            connection=CONNECTION, product=PRODUCT)
        defaults = {"vm_max": 3, "template_name": TEMPLATE}
        models.Profile.objects.update_or_create(name=TEST_PROFILE, hv=hv1,
                                                defaults=defaults)

    def tearDown(self):
        """ Remove any previous test profiles1. """

        try:
            profile1 = models.Profile.objects.get(name=TEST_PROFILE)
            for vm1 in models.Resource.objects.filter(profile=profile1):
                vm1.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            hv1 = models.HV.objects.get(connection=CONNECTION,
                                        product=PRODUCT)
            hv1.delete()
        except models.HV.DoesNotExist:
            pass

    def test_clone(self):
        """ test clone.

        Clone three resources. """
        count = 2

        hv1 = libvirt.open(CONNECTION)
        self.assertTrue(hv1)

        vmpool = kvm.api.Pool(CONNECTION, "test")
        self.assertTrue(vmpool)
        for item in range(count):
            vm_name = TEMPLATE + ".%d" % item
            try:
                vmpool.destroy(vm_name)
            except libvirt.libvirtError:
                continue

        pool = [item for item in vmpool.conn.listAllDomains()]
        pool = [item.name() for item in pool]
        pool = [item for item in pool if item.startswith(TEMPLATE)]
        for item in range(count):
            vm_name = TEMPLATE + ".%d" % item
            if vm_name not in pool:
                logging.debug("creating %s", vm_name)
                vmpool.clone(TEMPLATE, vm_name)
                vmpool.start(vm_name)

        for item in range(count):
            vm_name = "%s.%d" % (TEMPLATE, item)
            try:
                vmpool.destroy(vm_name)
            except libvirt.libvirtError:
                continue

    def test_info(self):
        """ test_info """

        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        self.assertTrue(hndl.getInfo())
        self.assertTrue(hndl.getHostname())

    def test_storage(self):
        """ test_storage """
        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        for item in hndl.listDomainsID():
            dom = hndl.lookupByID(item)
            print "Active: Name: ", dom.name()
            print "Active: Info: ", dom.info()

    def test_destroy_missing(self):
        """ test_destroy_missing. """

        profile1 = models.Profile.objects.get(name=TEST_PROFILE)

        hv1 = kvm.api.pool_get(profile1)
        self.assertTrue(hv1)

        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        try:
            vm_name = "%s.destroy" % TEMPLATE
            hv1.start(vm_name)
        except libvirt.libvirtError:
            pass


# pylint: disable=R0903
class FakeArgs(object):
    """ Used in testing to pass values to server.main. """
    def __init__(self):
        self.count = 200
        self.sleep_time = 1
        self.max_sleep_time = 60
        self.min_sleep_time = 1
        self.setup = True
        self.verbose = 0
        self.cfg_file = ""


class TestsuiteServer(unittest.TestCase):
    """ Test model output. """

    def tearDown(self):
        """ Make sure profile is removed. """
        try:
            hv1 = models.HV.objects.get(connection=CONNECTION,
                                        product=PRODUCT)
            profile1 = models.Profile.objects.get(name=TEST_PROFILE, hv=hv1)
            vmpool = kvm.api.pool_get(profile1)
            algo.destroy(vmpool, profile1)

            profile1.delete()
        except models.HV.DoesNotExist:
            pass
        except models.Profile.DoesNotExist:
            pass

    def test_setup(self):
        """ test_setup. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)

        defaults = {"vm_max": 1, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        self.assertEqual(profile1.vm_set.all().count(), 1)

    def test_shrink(self):
        """ test_shrink. test when the profile shrinks. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 3, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()
        ##

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        exts = ext.api_ext_list()

        vmpool = exts[PRODUCT].pool_get(profile1)
        self.assertEqual(len(vmpool.list(profile1)), 2)

    def test_expand(self):
        """ test_expand. Check when profile increases. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 2, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        ##
        # Now expand to 3
        profile1.vm_max = 3
        profile1.save()
        ##

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        exts = ext.api_ext_list()
        vmpool = exts[PRODUCT].pool_get(profile1)
        self.assertEqual(len(vmpool.list(profile1)), 3)

    def test_expiration(self):
        """ test_expiration. """

        vm_max = 3

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": vm_max, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        vms = profile1.vm_set.filter(status=models.Resource.READY)
        self.assertEqual(len(vms), vm_max)

        vmh = vms[0]

        ##
        # Acquire for 3 seconds.
        vmh.transition(models.Resource.RESERVED, algo.ACTION_DESTROY, 3)
        time.sleep(5)
        args.setup = False
        args.count = 2
        args.sleep_time = 1
        args.max_sleep_time = 1
        args.min_sleep_time = 1
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        ##

        exts = ext.api_ext_list()
        server.adapt(exts)

        vms = profile1.vm_set.filter(status=models.Resource.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(vms.count(), 2)
        ##


if __name__ == "__main__":
    unittest.main()
