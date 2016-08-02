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
""" Test pool Server. """
import unittest
import time
import logging
import testpool.core.ext
import testpool.core.algo
import testpool.core.logger
from testpool.core import commands
from testpool.core import profile
from testpooldb import models

FOREVER = None
LOGGER = logging.getLogger()
logging.getLogger("django.db.backends").setLevel(logging.CRITICAL)


def args_process(args):
    """ Process any generic parameters. """

    testpool.core.logger.args_process(LOGGER, args)


def argparser():
    """Create server arg parser. """

    parser = commands.argparser("testpool")
    parser.add_argument('--count', type=int, default=FOREVER,
                        help="The numnber events to process and then quit."
                        "Used for debugging.")
    parser.add_argument('--sleep-time', type=int, default=60,
                        help="Time between checking for changes.")

    return parser


def adapt(exts):
    """ Check to see if the pools should change. """

    for profile1 in models.Profile.objects.all():
        ext = exts[profile1.hv.product]
        vmpool = ext.vmpool_get(profile1.hv.hostname, profile1.name)
        testpool.core.algo.adapt(vmpool, profile1)


def reclaim(exts):
    """ Reclaim any VMs released. """

    LOGGER.info("testpool reclaim started")

    for vm1 in models.VM.objects.filter(status=models.VM.RELEASED):
        LOGGER.info("loading %s %s %s", vm1.profile.hv.hostname,
                    vm1.profile.hv.product, vm1.name)
        ext = exts[vm1.profile.hv.product]
        vmpool = ext.vmpool_get(vm1.profile.hv.hostname, vm1.profile.name)

        testpool.core.algo.reclaim(vmpool, vm1)
        vm1.status = models.VM.FREE
        vm1.save()
    LOGGER.info("testpool reclaim ended")


def setup(exts):
    """ Run the setup of each hypervisor. """

    LOGGER.info("testpool setup started")
    for profile1 in models.Profile.objects.all():
        LOGGER.info("setup %s %s %s", profile1.name, profile1.template_name,
                    profile1.vm_max)
        ext = exts[profile1.hv.product]
        vmpool = ext.vmpool_get(profile1.hv.hostname, profile1.name)
        LOGGER.info("algo.setup %s %s", profile1.name, profile1.template_name)
        LOGGER.info("algo.setup HV %s %d VMs", profile1.hv, profile1.vm_max)

        testpool.core.algo.remove(vmpool, profile1)
    LOGGER.info("testpool setup ended")


def main(args):
    """ Main entry point for server. """

    count = args.count

    LOGGER.info("testpool server started")
    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    ##
    # Restart the daemon if extensions change.
    exts = testpool.core.ext.api_ext_list()
    #
    setup(exts)

    while count == FOREVER or count > 0:
        adapt(exts)
        reclaim(exts)
        if args.sleep_time > 0:
            LOGGER.info("testpool sleeping %s (seconds)", args.sleep_time)
            time.sleep(args.sleep_time)

        if count != FOREVER:
            count -= 1

    LOGGER.info("testpool server stopped")
    return 0


# pylint: disable=R0903
class FakeArgs(object):
    """ Used in testing to pass values to server.main. """
    def __init__(self):
        self.count = 1
        self.sleep_time = 0


class ModelTestCase(unittest.TestCase):
    """ Test model output. """

    @staticmethod
    def fake_args():
        """ Return fake args to pass to main. """
        return FakeArgs()

    def test_setup(self):
        """ test_setup. """

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")

        defaults = {"vm_max": 1, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="fake.profile.1", hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        profile1.delete()

    def tearDown(self):
        profile.profile_remove("localhost", "fake", "fake.profile.1")

    def test_shrink(self):
        """ test_shrink. """

        product = "fake"
        profile_name = "fake.profile.2"
        hostname = "localhost"

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": 10, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="fake.profile.2", hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        exts = testpool.core.ext.api_ext_list()

        vmpool = exts[product].vmpool_get(hostname, profile_name)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()

        adapt(exts)

        vmpool = exts[product].vmpool_get(hostname, profile_name)
        self.assertEqual(len(vmpool.vm_list()), 2)

    def test_expand(self):
        """ test_expand. """

        product = "fake"
        hostname = "localhost"
        profile_name = "fake.profile.3"

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": 3, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=profile_name, hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 12
        profile1.save()

        exts = testpool.core.ext.api_ext_list()
        adapt(exts)

        vmpool = exts[product].vmpool_get(hostname, profile_name)
        self.assertEqual(len(vmpool.vm_list()), 12)
