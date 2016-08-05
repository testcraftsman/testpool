"""
  Examples on how to call the REST interfaces.

  The database needs to be running in order for these examples can run.

  tpl-db runserver
"""
import json
import unittest
import requests
import testpool.core.commands


TEST_URL = "http://127.0.0.1:8000/testpool/api/"


class Testsuite(unittest.TestCase):
    """ Demonstrate each REST interface. """

    def setup(self):
        """ Create a profile. """

        arg_parser = testpool.core.commands.main()
        cmd = "profile add localhost fake fake.profile fake.template 10"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(testpool.core.commands.args_process(args), 0)

    def test_profile_list(self):
        """ test_profile_list. """

        url = TEST_URL + "profile/list"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "fake.profile")

        self.assertTrue("vm_max" in profiles[0])
        self.assertTrue("vm_free" in profiles[0])

    def test_profile_acquire(self):
        """ test_profile_acquire acquire a VM. """

        url = TEST_URL + "profile/acquire"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "fake.profile")
