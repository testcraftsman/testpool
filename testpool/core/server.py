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
""" Test pool Server.

Server algorithm. VMs, given a current state, can be assigned an action
and when the action should fire.

STATE    ACTION    SUCCESS   STATE    FAILURE
PENDING  destroy   clone  PENDING  N attempts then mark BAD
PENDING  clone     attr   PENDING  N attempst then mark BAD
PENDING  attr      ready  READY    N attempst then mark BAD
RESERVED destroy   clone  PENDING  N attempts then mark BAD
"""
import datetime
import unittest
import time
import testpool.settings
import testpool.core.ext
import testpool.core.algo
from testpool.core import logger
from testpool.core import commands
from testpool.core import profile
from testpooldb import models

FOREVER = None
LOGGER = logger.create()


# pylint: disable=W0703
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

    LOGGER.info("adapt started")

    for profile1 in models.Profile.objects.all():
        ext = exts[profile1.hv.product]
        vmpool = ext.vmpool_get(profile1)
        testpool.core.algo.adapt(vmpool, profile1)

    LOGGER.info("adapt ended")


def action_destroy(exts, vmh):
    """ Reclaim any VMs released. """

    LOGGER.info("%s: action_destroy started %s %s %s",
                vmh.profile.name, vmh.profile.hv.hostname,
                vmh.profile.hv.product, vmh.name)

    ext = exts[vmh.profile.hv.product]
    vmpool = ext.vmpool_get(vmh.profile)

    try:
        testpool.core.algo.vm_destroy(vmpool, vmh)
        testpool.core.algo.adapt(vmpool, vmh.profile)
        LOGGER.info("%s: action_destroy %s done", vmh.profile.name,
                    vmh.name)
    except Exception:
        LOGGER.debug("%s: action_destroy %s interrupted", vmh.profile.name,
                     vmh.name)
        vmh.transition(vmh.status, vmh.action, 60)


def action_clone(exts, vmh):
    """ Clone a new VM. """

    LOGGER.info("%s: action_clone started %s %s %s",
                vmh.profile.name, vmh.profile.hv.hostname,
                vmh.profile.hv.product, vmh.name)

    ext = exts[vmh.profile.hv.product]
    vmpool = ext.vmpool_get(vmh.profile)
    try:
        testpool.core.algo.vm_clone(vmpool, vmh)
        testpool.core.algo.adapt(vmpool, vmh.profile)
    except Exception:
        LOGGER.debug("%s: action_clone %s interrupted", vmh.profile.name,
                     vmh.name)
        vmh.transition(vmh.status, vmh.action, 60)

    LOGGER.info("%s: action_clone done", vmh.profile.name)


def setup(_):
    """ Run the setup of each hypervisor.

    VMs are reset to pending with the action to destroy them.
    """

    LOGGER.info("setup started")

    for profile1 in models.Profile.objects.all():
        LOGGER.info("setup %s %s %s", profile1.name, profile1.template_name,
                    profile1.vm_max)
        ##
        # Quickly go through all of the VMs to reclaim them by transitioning.
        # them to PENDING and action destroy
        delta = 0
        for vmh in profile1.vm_set.all():
            vmh.transition(models.VM.RESERVED,
                           testpool.core.algo.ACTION_DESTROY, delta)
            delta += 60
        ##
    LOGGER.info("setup ended")


def action_attr(exts, vmh):
    """ Retrieve attributes. """

    LOGGER.info("%s: action_attr started %s %s %s",
                vmh.profile.name, vmh.profile.hv.hostname,
                vmh.profile.hv.product, vmh.name)

    ##
    #  If VM expires reclaim it.
    ext = exts[vmh.profile.hv.product]
    vmpool = ext.vmpool_get(vmh.profile)
    vmh.ip_addr = vmpool.ip_get(vmh.name)
    if vmh.ip_addr:
        LOGGER.info("%s: VM %s ip %s", vmh.profile.name, vmh.name,
                    vmh.ip_addr)
        vmh.transition(models.VM.READY, testpool.core.algo.ACTION_NONE, 1)
        adapt(exts)
    else:
        LOGGER.info("%s: VM %s waiting for ip addr", vmh.profile.name,
                    vmh.name)
        vmh.transition(vmh.status, vmh.action, 60)
    ##
    LOGGER.info("%s: action_attr ended", vmh.profile.name)


def events_show(banner):
    """ Show all of the pending events. """
    for vmh in models.VM.objects.exclude(
            status=models.VM.READY).order_by("action_time"):
        action_delay = vmh.action_time - datetime.datetime.now()
        action_delay = action_delay.seconds

        LOGGER.info("%s: %s %s action %s at %s", vmh.name, banner,
                    models.VM.status_to_str(vmh.status), vmh.action,
                    vmh.action_time)


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
    events_show("after setup")
    adapt(exts)
    events_show("after adapt")

    while count == FOREVER or count > 0:
        events_show("while loop")

        current = datetime.datetime.now()
        vmh = models.VM.objects.exclude(
            status=models.VM.READY).order_by("action_time").first()

        if not vmh:
            sleep_time = 60
            LOGGER.info("testpool no actions sleeping %s (seconds)",
                        sleep_time)
            time.sleep(sleep_time)
        elif vmh.action_time < current:
            LOGGER.info("%s: status %s action %s at %s", vmh.name,
                        models.VM.status_to_str(vmh.status), vmh.action,
                        vmh.action_time)
            LOGGER.info("%s: %s at %s", vmh.name, vmh.action, vmh.action_time)
            if vmh.action == testpool.core.algo.ACTION_DESTROY:
                action_destroy(exts, vmh)
            elif vmh.action == testpool.core.algo.ACTION_CLONE:
                action_clone(exts, vmh)
            elif vmh.action == testpool.core.algo.ACTION_ATTR:
                action_attr(exts, vmh)
            elif vmh.action == testpool.core.algo.ACTION_NONE:
                pass
            else:
                LOGGER.error("%s: unknown action %s", vmh.name, vmh.action)
        else:
            action_delay = abs(vmh.action_time - current).seconds
            sleep_time = min(60, action_delay)
            sleep_time = max(1, sleep_time)
            LOGGER.info("testpool sleeping %s (seconds)", sleep_time)
            time.sleep(sleep_time)

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
        profile.profile_remove("localhost", "fake.profile.1")

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

    def test_expiration(self):
        """ test_expiration. """

        product = "fake"
        hostname = "localhost"
        profile_name = "fake.profile.4"

        (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                                   product=product)
        defaults = {"vm_max": 3, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=profile_name, hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

        vms = profile1.vm_set.filter(status=models.VM.PENDING)
        vmh = vms[0]
        ##
        # Acquire for 3 seconds.
        vmh.acquire(3)
        ##
        time.sleep(5)

        exts = testpool.core.ext.api_ext_list()
        adapt(exts)

        vms = profile1.vm_set.filter(status=models.VM.PENDING)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(vms.count(), 3)
        ##
