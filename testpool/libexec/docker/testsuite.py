# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testpool
#
# Testbed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Testbed is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Testdb.  If not, see <http://www.gnu.org/licenses/>.

"""
Test docker API

Install python binding to docker.
  - sudo -H pip install docker
"""

import time
import unittest
import logging
import docker
from testpooldb import models
from testpool.core import server
from testpool.core import ext
from testpool.core import algo
from testpool.libexec.docker import api

CONNECTION = "http://127.0.0.1"
TEST_PROFILE = "test.docker.profile"
##
# Used nginx because it does not terminate.
TEMPLATE = "nginx:1.13"
##

PRODUCT = "docker"


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a container. """

    def setUp(self):
        """ Create docker profile. """

        (hv1, _) = models.HV.objects.get_or_create(
            connection=CONNECTION, product=PRODUCT)
        defaults = {"vm_max": 3, "template_name": TEMPLATE}
        models.Profile.objects.update_or_create(name=TEST_PROFILE, hv=hv1,
                                                defaults=defaults)

    def tearDown(self):
        """ Remove any previous test profiles1. """
        logging.debug("tearDown")

        try:
            profile1 = models.Profile.objects.get(name=TEST_PROFILE)
            for vm1 in models.VM.objects.filter(profile=profile1):
                vm1.delete()
            profile1.delete()
        except models.Profile.DoesNotExist:
            pass

        try:
            hv1 = models.HV.objects.get(connection=CONNECTION, product=PRODUCT)
            hv1.delete()
        except models.HV.DoesNotExist:
            pass

    def test_clone(self):
        """ test creating a container given an image. """

        count = 3

        hv1 = docker.from_env()
        self.assertTrue(hv1)

        vmpool = api.VMPool(CONNECTION, "test")
        self.assertIsNotNone(vmpool)
        for item in range(count):
            vm_name = vmpool.new_name_get(TEMPLATE, item)
            vmpool.destroy(vm_name)

        pool = [item for item in vmpool.conn.containers.list()]
        for item in range(count):
            vm_name = vmpool.new_name_get(TEMPLATE, item)
            if vm_name not in pool:
                logging.debug("cloning %s to %s", TEMPLATE, vm_name)
                vmpool.clone(TEMPLATE, vm_name)
                vmpool.start(vm_name)

        for item in range(count):
            vm_name = TEMPLATE + ".%d" % item
            vmpool.destroy(vm_name)

    def test_destroy_missing(self):
        """ test_destroy_missing. """

        profile1 = models.Profile.objects.get(name=TEST_PROFILE)

        hv1 = api.vmpool_get(profile1)
        self.assertTrue(hv1)

        vm_name = "%s.destroy" % TEMPLATE
        hv1.destroy(vm_name)


# pylint: disable=R0903
class FakeArgs(object):
    """ Used in testing to pass values to server.main. """
    def __init__(self):
        self.count = 40
        self.sleep_time = 1
        self.max_sleep_time = 60
        self.min_sleep_time = 1
        self.setup = True
        self.verbose = 3
        self.cfg_file = ""


class TestsuiteServer(unittest.TestCase):
    """ Test model output. """

    def tearDown(self):
        """ Make sure profile is removed. """

        try:
            hv1 = models.HV.objects.get(connection=CONNECTION,
                                        product=PRODUCT)
            profile1 = models.Profile.objects.get(name=TEST_PROFILE, hv=hv1)
            vmpool = api.vmpool_get(profile1)
            algo.destroy(vmpool, profile1)
            profile1.delete()
        except models.HV.DoesNotExist:
            pass
        except models.Profile.DoesNotExist:
            pass

        hv1 = docker.from_env()
        vmpool = api.VMPool(CONNECTION, "test")

    def test_setup(self):
        """ test_setup. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)

        defaults = {"vm_max": 1, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        self.assertEqual(profile1.vm_set.all().count(), 1)

    def test_create_one(self):
        """ Create one container. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 1, "template_name": TEMPLATE}
        models.Profile.objects.update_or_create(name=TEST_PROFILE, hv=hv1,
                                                defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

    def test_create_two(self):
        """ Create one container. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 2, "template_name": TEMPLATE}
        models.Profile.objects.update_or_create(name=TEST_PROFILE, hv=hv1,
                                                defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

    def test_shrink(self):
        """ test_shrink. test when the profile shrinks. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 3, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()
        ##

        args = FakeArgs()
        args.setup = False
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        exts = ext.api_ext_list()

        vmpool = exts[PRODUCT].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list(profile1)), 2)

    def test_expand(self):
        """ test_expand. Check when profile increases. """

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": 2, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        ##
        #  Now expand to 3
        profile1.vm_max = 3
        profile1.save()
        ##

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        exts = ext.api_ext_list()
        vmpool = exts[PRODUCT].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list(profile1)), 3)

    def test_expiration(self):
        """ test_expiration. """

        vm_max = 3

        (hv1, _) = models.HV.objects.get_or_create(connection=CONNECTION,
                                                   product=PRODUCT)
        defaults = {"vm_max": vm_max, "template_name": TEMPLATE}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=TEST_PROFILE, hv=hv1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        vms = profile1.vm_set.filter(status=models.VM.READY)
        self.assertEqual(len(vms), vm_max)

        vmh = vms[0]

        ##
        # Acquire for 3 seconds.
        vmh.transition(models.VM.RESERVED, algo.ACTION_DESTROY, 3)
        time.sleep(5)
        args.setup = False
        args.count = 2
        args.sleep_time = 1
        args.max_sleep_time = 1
        args.min_sleep_time = 1
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        ##

        exts = ext.api_ext_list()
        server.adapt(exts)

        vms = profile1.vm_set.filter(status=models.VM.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(vms.count(), 2)
        ##


if __name__ == "__main__":
    unittest.main()
