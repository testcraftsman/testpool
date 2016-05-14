"""
Tests KVM API
"""
import unittest
import logging
import libvirt
import testpool.core.db
import api

class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a VM. """

    def test_setup(self):
        """ test clone """

        rtc = testpool.db.setup(api.VMPool(), "localhost", "profile1",
                                "template", 10)
        self.assertEqual(rtc, 0)

if __name__ == "__main__":
    unittest.main()
