"""
Test fake API.

Useful for developing Testpool algorithms.
"""
import unittest
import logging
from testpool.core import ext
from testpool.core import algo
from testpool.core import database
from testpool.core import server
from testpool.libexec.fake import api

##
# database init is required to add to the system path so that models can
# be found
# pylint: disable=C0413
database.init()  # nopep8
from testpooldb import models
##


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a resource. """

    def test_setup(self):
        """ test clone """

        (hv1, _) = models.HV.objects.get_or_create(connection="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", hv=hv1, template_name="test.template",
            vm_max=10)

        vmpool = api.Pool("fake.profile")
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

    def test_pop(self):
        """ test_pop Popping resources. """

        (hv1, _) = models.HV.objects.get_or_create(connection="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", hv=hv1, template_name="test.template",
            vm_max=10)
        vmpool = api.Pool("fake.profile")

        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)
            vm1 = algo.pop("fake.profile", 1)
            self.assertTrue(vm1)

        with self.assertRaises(algo.NoResources):
            algo.pop("fake.profile", 1)

    def test_push(self):
        """ test_push. """

        profile_name = "fake.profile"

        (hv1, _) = models.HV.objects.get_or_create(connection="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", hv=hv1, vm_max=10,
            template_name="test.template")

        vmpool = api.Pool("memory")
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)

            vm1 = algo.pop(profile_name, 1)
            self.assertTrue(vm1)

        with self.assertRaises(algo.NoResources):
            algo.pop(profile_name, 1)

    def test_push_too_many(self):
        """ test_push_too_many"""

        profile_name = "fake.profile"

        (hv1, _) = models.HV.objects.get_or_create(connection="localhost",
                                                   product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", hv=hv1, template_name="test.template",
            vm_max=10)

        vmpool = api.pool_get(profile1)
        self.assertTrue(vmpool)
        algo.destroy(vmpool, profile1)
        rtc = algo.adapt(vmpool, profile1)
        self.assertEqual(rtc, 10)

        vm1 = algo.pop(profile_name, 1)
        self.assertTrue(vm1)

        algo.push(vm1.id)
        with self.assertRaises(algo.ResourceReleased):
            algo.push(vm1.id)

        api_exts = ext.api_ext_list()
        server.adapt(api_exts)

    def tearDown(self):
        """ Remove any previous fake profiles1. """

        try:
            profile1 = models.Profile.objects.get(name="fake.profile")
            for vm1 in models.Resource.objects.filter(profile=profile1):
                vm1.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            hv1 = models.HV.objects.get(connection="localhost", product="fake")
            hv1.delete()
        except models.HV.DoesNotExist:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
