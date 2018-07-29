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

        (host1, _) = models.Host.objects.get_or_create(connection="localhost",
                                                       product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", host=host1, template_name="test.template",
            resource_max=10)

        pool = api.Pool("fake.profile")
        algo.destroy(pool, profile1)
        rtc = algo.adapt(pool, profile1)
        self.assertEqual(rtc, 10)

    def test_pop(self):
        """ test_pop Popping resources. """

        (host1, _) = models.Host.objects.get_or_create(connection="localhost",
                                                       product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", host=host1, template_name="test.template",
            resource_max=10)
        pool = api.Pool("fake.profile")

        algo.destroy(pool, profile1)
        rtc = algo.adapt(pool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)
            rsrc = algo.pop("fake.profile", 1)
            self.assertTrue(rsrc)

        with self.assertRaises(algo.NoResources):
            algo.pop("fake.profile", 1)

    def test_push(self):
        """ test_push. """

        profile_name = "fake.profile"

        (host1, _) = models.Host.objects.get_or_create(connection="localhost",
                                                       product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", host=host1, resource_max=10,
            template_name="test.template")

        pool = api.Pool("memory")
        algo.destroy(pool, profile1)
        rtc = algo.adapt(pool, profile1)
        self.assertEqual(rtc, 10)

        for count in range(10):
            logging.debug("pop count %d", count)

            rsrc = algo.pop(profile_name, 1)
            self.assertTrue(rsrc)

        with self.assertRaises(algo.NoResources):
            algo.pop(profile_name, 1)

    def test_push_too_many(self):
        """ test_push_too_many"""

        profile_name = "fake.profile"

        (host1, _) = models.Host.objects.get_or_create(connection="localhost",
                                                       product="fake")
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile", host=host1, template_name="test.template",
            resource_max=10)

        pool = api.pool_get(profile1)
        self.assertTrue(pool)
        algo.destroy(pool, profile1)
        rtc = algo.adapt(pool, profile1)
        self.assertEqual(rtc, 10)

        rsrc = algo.pop(profile_name, 1)
        self.assertTrue(rsrc)

        algo.push(rsrc.id)
        with self.assertRaises(algo.ResourceReleased):
            algo.push(rsrc.id)

        api_exts = ext.api_ext_list()
        server.adapt(api_exts)

    def tearDown(self):
        """ Remove any previous fake profiles1. """

        try:
            profile1 = models.Profile.objects.get(name="fake.profile")
            for rsrc in models.Resource.objects.filter(profile=profile1):
                rsrc.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            host1 = models.Host.objects.get(connection="localhost",
                                            product="fake")
            host1.delete()
        except models.Host.DoesNotExist:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
