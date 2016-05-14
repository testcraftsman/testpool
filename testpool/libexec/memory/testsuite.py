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

        rtc = testpool.core.algo.setup(api.VMPool("memory"), "localhost",
                                       "profile1", "template", 10)
        self.assertEqual(rtc, 0)

if __name__ == "__main__":
    testpool.core.database.init()
    unittest.main()
