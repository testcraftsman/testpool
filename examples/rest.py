"""
Examples on how to call the REST interfaces. Read the quick start guide in
order to configure Testpool server and then come back to this script.

As discussed in the Testpool quickstart guide. This example uses a
profile named example. These examples work best when all VMs have been cloned
and have retrieved their IP address.  Make sure VMs are avaliable, run:

  ./bin/tpl profile list

To run this file type

  py.test -s examples/python_api.py

These examples illustrates the use of the testpool.client. The global variable
GLOBAL in conftest defines the Testpool profile. Once a VM is acquired, this
test can login and use the VM throughout the entire testsuite. This assumes
that the VM has negotiated an IP address usually throught DHCP.

As these examples are running, use virt-manager to see hypervisor changes.
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
    """ Wrap acquire with a delay in case none are available. """
    ##
    # previous tests may have acquired all VMs wait for a while to
    # acquire one
    for _ in range(10):
        resp = requests.get(url)
        if resp.status_code == 403:
            time.sleep(60)
        else:
            rsrc = json.loads(resp.text)
            return rsrc
    resp.raise_for_status()
    ##
    return None


class Testsuite(unittest.TestCase):
    """ Demonstrate each REST interface. """

    def test_profile_list(self):
        """ test_profile_list Show how to list profile content."""

        url = TEST_URL + "profile/list"
        resp = requests.get(url)
        resp.raise_for_status()
        profiles = json.loads(resp.text)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "example")

        self.assertTrue("resource_max" in profiles[0])
        self.assertTrue("resource_ready" in profiles[0])

    def test_profile_acquire(self):
        """ test_profile_acquire acquire a VM. """

        url = TEST_URL + "profile/acquire/example"
        requests.get(url)
        rsrc = acquire_get(url)

        ##
        # Cloned VMs begin with the name of the template.
        self.assertTrue(rsrc["name"].startswith("test.template"))
        self.assertTrue(len(rsrc["name"]) > len("test.template"))
        ##

        rsrc2 = acquire_get(url)

        self.assertTrue(rsrc2["name"].startswith("test.template"))
        self.assertTrue(len(rsrc2["name"]) > len("test.template"))

        url = TEST_URL + "profile/release/%d" % rsrc["id"]
        acquire_get(url)

        url = TEST_URL + "profile/release/%d" % rsrc2["id"]
        acquire_get(url)

    def test_acquire_too_many(self):
        """ test_acquire_too_many attempt to acquire too many VMs."""

        prev_rsrcs = set()
        url = TEST_URL + "profile/acquire/example"

        ##
        # Take all of the VMs
        for _ in range(conftest.GLOBAL["count"]):
            rsrc = acquire_get(url)

            self.assertTrue(rsrc["name"].startswith("test.template"))
            self.assertFalse(rsrc["name"] in prev_rsrcs)

            prev_rsrcs.add(rsrc["id"])
        ##

        resp = requests.get(url)
        self.assertEqual(resp.status_code, 403)

        for rsrc_id in prev_rsrcs:
            url = TEST_URL + "profile/release/%d" % rsrc_id
            acquire_get(url)

    def test_acquire_renew(self):
        """ test_acquire_renew renew an acquired VM. """

        url = TEST_URL + "profile/acquire/example"

        rsrc = acquire_get(url)
        rsrc_id = rsrc["id"]

        url = TEST_URL + "resource/renew/%(id)s" % rsrc
        resp = requests.get(url)
        resp.raise_for_status()
        rsrc = json.loads(resp.text)
        self.assertEqual(rsrc["id"], rsrc_id)

        params = {"expiration": 100}
        resp = requests.get(url, urllib.urlencode(params))
        resp.raise_for_status()
        rsrc = json.loads(resp.text)
        self.assertEqual(rsrc["id"], rsrc_id)

        ##
        # Check to see if the expiration is roughly 100 seconds.
        timestamp = datetime.datetime.strptime(rsrc["action_time"],
                                               "%Y-%m-%dT%H:%M:%S.%f")
        expiration_time = timestamp - datetime.datetime.now()
        self.assertTrue(expiration_time.seconds <= 100)
        self.assertTrue(expiration_time.seconds >= 90)
        ##

        url = TEST_URL + "profile/release/%d" % rsrc_id
        resp = requests.get(url)
        resp.raise_for_status()
