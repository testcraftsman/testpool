"""
Tests KVM API
"""
import unittest
import logging
import testpool.core.database
import testpool.core.ext
from testpool.core import algo
import testpool.core.server
from testpool.libexec.fake import api
from testpooldb import models


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def test_setup(self):
        """ test clone """

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="test.profile1", hv=hv1, template_name="test.template",
            vm_max=10)

        vmpool = api.VMPool("memory")
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

    def test_pop(self):
        """ test_pop Popping resources. """

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="test.profile1", hv=hv1, template_name="test.template",
            vm_max=10)
        vmpool = api.VMPool("memory")

        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)
            vm1 = algo.pop("localhost", "fake", "test.profile1", 1)
            self.assertTrue(vm1)

        with self.assertRaises(algo.NoResources):
            algo.pop("localhost", "fake", "test.profile1", 1)

    def test_push(self):
        """ test_push. """

        profile_name = "test.profile1"

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="test.profile1", hv=hv1, vm_max=10,
            template_name="test.template")

        vmpool = api.VMPool("memory")
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)

            vm1 = algo.pop("localhost", "fake", profile_name, 1)
            self.assertTrue(vm1)

        with self.assertRaises(algo.NoResources):
            algo.pop("localhost", "fake", profile_name, 1)

    def test_push_too_many(self):
        """ test_push_too_many"""

        profile_name = "test.profile1"

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="test.profile1", hv=hv1, template_name="test.template",
            vm_max=10)

        vmpool = api.vmpool_get(profile1)
        self.assertTrue(vmpool)
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        vm1 = algo.pop("localhost", "fake", profile_name, 1)
        self.assertTrue(vm1)

        algo.push(vm1.id)
        with self.assertRaises(algo.ResourceReleased):
            algo.push(vm1.id)

        api_exts = testpool.core.ext.api_ext_list()
        testpool.core.server.adapt(api_exts)

    def tearDown(self):
        """ Remove any previous test profiles1. """

        try:
            profile1 = models.Profile.objects.get(name="test.profile1")
            for vm1 in models.VM.objects.filter(profile=profile1):
                vm1.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            hv1 = models.HV.objects.get(hostname="localhost", product="fake")
            hv1.delete()
        except models.HV.DoesNotExist:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
