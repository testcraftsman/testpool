"""
Tests KVM API
"""
import unittest
import logging
import libvirt
import testpool.core.database
import api


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def test_setup(self):
        """ test clone """
        import testpool.core.algo

        rtc = testpool.core.algo.setup(api.VMPool("memory"), "profile1",
                                       "template", 10)
        self.assertEqual(rtc, 0)

    def test_pop(self):
        """ test_pop Popping resources. """

        import testpool.core.algo

        rtc = testpool.core.algo.setup(api.VMPool("memory"), "profile1",
                                       "template", 10)
        self.assertEqual(rtc, 0)

        for count in range(10):
            logging.debug("pop count %d", count)

            vm = testpool.core.algo.pop("profile1")
            self.assertTrue(vm)

        with self.assertRaises(testpool.core.algo.NoResources) as check:
            testpool.core.algo.pop("profile1")

    def test_push(self):
        """ test_push"""

        import testpool.core.algo

        rtc = testpool.core.algo.setup(api.VMPool("memory"), "profile1",
                                       "template", 10)
        self.assertEqual(rtc, 0)

        for count in range(10):
            logging.debug("pop count %d", count)

            vm = testpool.core.algo.pop("profile1")
            self.assertTrue(vm)
            testpool.core.algo.push(vm.id)

        with self.assertRaises(testpool.core.algo.NoResources) as check:
            testpool.core.algo.pop("profile1")

    def test_push_too_many(self):
        """ test_push_too_many"""

        import testpool.core.algo

        rtc = testpool.core.algo.setup(api.VMPool("memory"), "profile1",
                                       "template", 10)
        self.assertEqual(rtc, 0)

        vm = testpool.core.algo.pop("profile1")
        self.assertTrue(vm)
        testpool.core.algo.push(vm.id)
        with self.assertRaises(testpool.core.algo.ResourceReleased) as check:
            testpool.core.algo.push(vm.id)

if __name__ == "__main__":
    testpool.core.database.init()
    unittest.main()
