"""
Tests KVM API
"""
import unittest
import logging
import testpool.core.database
import testpool.core.ext
import testpool.core.algo
from testpool.libexec.fake import api
from testpooldb import models


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def test_setup(self):
        """ test clone """

        profile1 = models.VM.objects.create(name="test.profile1",
                                            template_name="test.template",
                                            vm_max=10)
        rtc = testpool.core.algo.setup(api.VMPool("memory"), profile1)
        self.assertEqual(rtc, 0)

    def test_pop(self):
        """ test_pop Popping resources. """

        profile1 = models.VM.objects.create(name="test.profile1",
                                            template_name="test.template",
                                            vm_max=10)
        vmpool = api.VMPool("memory")
        rtc = testpool.core.algo.setup(vmpool, profile1)
        self.assertEqual(rtc, 0)

        for count in range(10):
            logging.debug("pop count %d", count)
            vm1 = testpool.core.algo.pop(vmpool, "test.profile1")
            self.assertTrue(vm1)

        with self.assertRaises(testpool.core.algo.NoResources):
            testpool.core.algo.pop(vmpool, "test.profile1")

    def test_push(self):
        """ test_push"""

        profile_name = "test.profile1"
        profile1 = models.VM.objects.create(name="test.profile1",
                                            template_name="test.template",
                                            vm_max=10)

        vmpool = api.VMPool("memory")
        rtc = testpool.core.algo.setup(vmpool, profile1)
        self.assertEqual(rtc, 0)

        for count in range(10):
            logging.debug("pop count %d", count)

            vm1 = testpool.core.algo.pop(vmpool, profile_name)
            self.assertTrue(vm1)
            testpool.core.algo.push(vmpool, vm1.id)

        with self.assertRaises(testpool.core.algo.NoResources):
            testpool.core.algo.pop(vmpool, profile_name)

    def test_push_too_many(self):
        """ test_push_too_many"""

        profile1 = models.VM.objects.create(name="test.profile1",
                                            template_name="test.template",
                                            vm_max=10)

        vmpool = api.vmpool_get("memory")
        self.assertTrue(vmpool)

        rtc = testpool.core.algo.setup(vmpool, profile1)
        self.assertEqual(rtc, 0)

        vm1 = testpool.core.algo.pop(vmpool, "test.profile1")
        self.assertTrue(vm1)

        testpool.core.algo.push(vmpool, vm1.id)
        with self.assertRaises(testpool.core.algo.ResourceReleased):
            testpool.core.algo.push(vmpool, vm1.id)

        api_exts = testpool.core.ext.ext_list()
        testpool.core.server.reclaim(api_exts)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
