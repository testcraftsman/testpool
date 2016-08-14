"""
  Examples on how to call the REST interfaces.

  The database needs to be running in order for these examples can run.
"""
import json
import unittest
import requests
import testpool.core.commands
import testpool.core.server


TEST_URL = "http://127.0.0.1:8000/testpool/api/"


def setup_module():
    """ Create a profile. """

    ##
    # Add a fake.profile to the database.
    arg_parser = testpool.core.commands.main()
    cmd = "profile add localhost fake fake.profile fake.template 10"
    args = arg_parser.parse_args(cmd.split())
    assert testpool.core.commands.args_process(args) == 0
    ##

    ##
    # Use the existing core server code to create all of the VMs for the
    # above fake profile.
    arg_parser = testpool.core.server.argparser()
    cmd = "--count 1 --verbose --sleep-time 0"
    args = arg_parser.parse_args(cmd.split())
    testpool.core.server.args_process(args)
    testpool.core.server.main(args)
    ##


def teardown_module():
    """ Create a profile. """

    arg_parser = testpool.core.commands.main()
    cmd = "profile remove localhost fake.profile"
    args = arg_parser.parse_args(cmd.split())
    assert testpool.core.commands.args_process(args) == 0


class Testsuite(unittest.TestCase):
    """ Demonstrate each REST interface. """

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

        url = TEST_URL + "profile/acquire/fake.profile"
        resp = requests.get(url)
        resp.raise_for_status()
        vm1 = json.loads(resp.text)

        self.assertTrue(vm1["name"].startswith("fake.template"))
        self.assertTrue(len(vm1["name"]) > len("fake.template"))

        resp = requests.get(url)
        resp.raise_for_status()
        vm2 = json.loads(resp.text)

        self.assertTrue(vm2["name"].startswith("fake.template"))
        self.assertTrue(len(vm2["name"]) > len("fake.template"))

        url = TEST_URL + "profile/release/%d" % vm1["id"]
        resp = requests.get(url)
        resp.raise_for_status()

        url = TEST_URL + "profile/release/%d" % vm2["id"]
        resp = requests.get(url)
        resp.raise_for_status()
