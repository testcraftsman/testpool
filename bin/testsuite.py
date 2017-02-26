"""
Test content in the bin directory.
"""
import os
import subprocess
import unittest
import yaml
import tplcfgcheck


class Testsuite(unittest.TestCase):
    """ Testsuite framework. """

    def test_configuration(self):
        """ test configuration file. """

        data = {
            "tpldaemon": {
                "profile": {
                    "log": "/etc/testpool/testpool.yml"
                }
            }
        }

        rtc = tplcfgcheck.check_level(data, tplcfgcheck.VALID, None)
        self.assertEqual(rtc, 0)

        data = {
            "tpldaemon": {
                "profile": {
                    "log": 1.2
                }
            }
        }
        rtc = tplcfgcheck.check_level(data, tplcfgcheck.VALID, None)
        self.assertEqual(rtc, 1)

    def test_current(self):
        """ test current configuration. """

        rtc = os.system("git rev-parse --is-inside-work-tree")
        self.assertEqual(rtc, 0)

        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        root = root[:-1]
        path = os.path.join(root, "etc", "testpool", "testpool.yml")
        with open(path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            rtc = tplcfgcheck.check_level(cfg, tplcfgcheck.VALID, None)
            self.assertEqual(rtc, 0)
