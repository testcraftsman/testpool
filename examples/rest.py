"""
  Examples on how to call the REST interfaces.

  The database needs to be running in order for these examples can run.
"""
import json
import datetime
import urllib
import unittest
import requests
import testpool.core.commands
import testpool.core.server


TEST_URL = "http://127.0.0.1:8000/testpool/api/"

VM_COUNT = 10


class Testsuite(unittest.TestCase):
    """ Demonstrate each REST interface. """

    def tearDown(self):
        """ Delete the fake test profile. """

        arg_parser = testpool.core.commands.main()
        cmd = "profile remove localhost test.profile"
        args = arg_parser.parse_args(cmd.split())
        assert testpool.core.commands.args_process(None, args) == 0

    def test_profile_list(self):
        """ test_profile_list. """

        url = TEST_URL + "profile/list"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "test.profile")

        self.assertTrue("vm_max" in profiles[0])
        self.assertTrue("vm_ready" in profiles[0])

    def test_profile_acquire(self):
        """ test_profile_acquire acquire a VM. """

        url = TEST_URL + "profile/acquire/test.profile"
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

    def test_acquire_too_many(self):
        """ test_profile_acquire_too_many attempt to acquire more than 10."""

        prev_vms = set()
        url = TEST_URL + "profile/acquire/test.profile"

        ##
        # Take all of the VMs
        for _ in range(VM_COUNT):
            resp = requests.get(url)
            resp.raise_for_status()
            vm1 = json.loads(resp.text)

            self.assertTrue(vm1["name"].startswith("fake.template"))
            self.assertFalse(vm1["name"] in prev_vms)

            prev_vms.add(vm1["name"])
        ##

        resp = requests.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_acquire_renew(self):
        """ test_acquire_renew renew an acquired VM. """

        url = TEST_URL + "profile/acquire/test.profile"

        resp = requests.get(url)
        resp.raise_for_status()
        vm1 = json.loads(resp.text)
        vm_id = vm1["id"]

        url = TEST_URL + "vm/renew/%(id)s" % vm1
        resp = requests.get(url)
        resp.raise_for_status()
        vm1 = json.loads(resp.text)
        self.assertEqual(vm1["id"], vm_id)

        params = {"expiration": 100}
        resp = requests.get(url, urllib.urlencode(params))
        resp.raise_for_status()
        vm1 = json.loads(resp.text)
        self.assertEqual(vm1["id"], vm_id)

        ##
        # Check to see if the expiration is roughly 100 seconds.
        timestamp = datetime.datetime.strptime(vm1["reserved"],
                                               "%Y-%m-%dT%H:%M:%S.%f")
        expiration_time = timestamp - datetime.datetime.now()
        self.assertTrue(expiration_time.seconds < 100)
        self.assertTrue(expiration_time.seconds > 90)
        ##
