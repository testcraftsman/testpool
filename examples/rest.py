"""
  Examples on how to call the REST interfaces.

  The database needs to be running in order for these examples can run.
"""
import time
import json
import datetime
import urllib
import unittest
import requests
import conftest


TEST_URL = "http://%(hostname)s:8000/testpool/api/" % conftest.GLOBAL


def acquire_get(url):
    """ Wrap acquire with a delay incase none are available. """
    ##
    # previous tests may have acquired all VMs wait for a while to
    # acquire one
    for _ in range(10):
        resp = requests.get(url)
        if resp.status_code == 403:
            time.sleep(60)
        else:
            vm1 = json.loads(resp.text)
            return vm1
    resp.raise_for_status()
    ##


class Testsuite(unittest.TestCase):
    """ Demonstrate each REST interface. """

    def test_profile_list(self):
        """ test_profile_list. """

        url = TEST_URL + "profile/list"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "example")

        self.assertTrue("vm_max" in profiles[0])
        self.assertTrue("vm_ready" in profiles[0])

    def test_profile_acquire(self):
        """ test_profile_acquire acquire a VM. """

        url = TEST_URL + "profile/acquire/example"
        requests.get(url)
        vm1 = acquire_get(url)

        self.assertTrue(vm1["name"].startswith("test.template"))
        self.assertTrue(len(vm1["name"]) > len("test.template"))

        vm2 = acquire_get(url)

        self.assertTrue(vm2["name"].startswith("test.template"))
        self.assertTrue(len(vm2["name"]) > len("test.template"))

        url = TEST_URL + "profile/release/%d" % vm1["id"]
        acquire_get(url)

        url = TEST_URL + "profile/release/%d" % vm2["id"]
        acquire_get(url)

    def test_acquire_too_many(self):
        """ test_acquire_too_many attempt to acquire too many VMs."""

        prev_vms = set()
        url = TEST_URL + "profile/acquire/example"

        ##
        # Take all of the VMs
        for _ in range(conftest.GLOBAL["count"]):
            vm1 = acquire_get(url)

            self.assertTrue(vm1["name"].startswith("test.template"))
            self.assertFalse(vm1["name"] in prev_vms)

            prev_vms.add(vm1["id"])
        ##

        resp = requests.get(url)
        self.assertEqual(resp.status_code, 403)

        for vm_id in prev_vms:
            url = TEST_URL + "profile/release/%d" % vm_id
            acquire_get(url)

    def test_acquire_renew(self):
        """ test_acquire_renew renew an acquired VM. """

        url = TEST_URL + "profile/acquire/example"

        vm1 = acquire_get(url)
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
        timestamp = datetime.datetime.strptime(vm1["action_time"],
                                               "%Y-%m-%dT%H:%M:%S.%f")
        expiration_time = timestamp - datetime.datetime.now()
        self.assertTrue(expiration_time.seconds <= 100)
        self.assertTrue(expiration_time.seconds >= 90)
        ##

        url = TEST_URL + "profile/release/%d" % vm_id
        resp = requests.get(url)
        resp.raise_for_status()
