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

STATE    ACTION    STATE    NEXT ACTION   FAILURE
PENDING  destroy   PENDING  clone         N attempts then mark BAD
PENDING  clone     PENDING  attr          N attempst then mark BAD
PENDING  attr      READY    ready         N attempst then mark BAD
READY    acquire   RESERVED pushed,  timeout or renew
RESERVED pushed    PENDING  destroy
RESERVED timeout   PENDING  destroy       N attempts then mark BAD
"""
import datetime
import os
import unittest
import time
import logging
import structlog
import testpool.settings
from testpool.core import ext
from testpool.core import algo
from testpool.core import api
from testpool.core import logger
from testpool.core import commands
from testpool.core import profile
from testpool.core import exceptions
from testpool.core import coding
from testpool.core import cfgcheck
from testpooldb import models

FOREVER = None
CFG = None
LOGGER = logger.create()
PROFILE_LOGGER = None


class NullHandler(logging.Handler):
    """ Supress warning messages. """
    def emit(self, record):
        pass


def profile_log_create(log_file):
    """ Create structured log. """

    if not log_file:
        return None

    ##
    # Timestamper must use utc=True because the golang parsing
    # code really expects RFC3339Nano which is a version of 
    # iso8601.
    log = logging.getLogger()
    log.addHandler(logging.FileHandler(log_file))
    log.setLevel(logging.INFO)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    ##

    return structlog.wrap_logger(log)


# pylint: disable=R0912
# pylint: disable=W0703
# pylint: disable=W0603
def args_process(args):
    """ Process any generic parameters.

    Read configuration file /etc/testpool/testpool.yml. Check if configuration
    file exists, if so load it and validate its content.
    """

    global CFG
    global PROFILE_LOGGER

    testpool.core.logger.args_process(LOGGER, args)
    ##
    # After this we know that the configuration is valid.
    CFG = cfgcheck.check(args.cfg)
    if CFG:
        LOGGER.info("loading configuration file %s", args.cfg)
    else:
        LOGGER.warning("configuration file %s not found", args.cfg)
    try:
        PROFILE_LOGGER = profile_log_create(CFG.tpldaemon.profile.log)
    except AttributeError:
        pass


def argparser():
    """Create server arg parser. """

    parser = commands.argparser("testpool")
    parser.add_argument('--count', type=int, default=FOREVER,
                        help="The numnber events to process and then quit."
                        "Used for debugging.")
    parser.add_argument('--max-sleep-time', type=int, default=60,
                        help="Maximum time between checking for changes.")
    parser.add_argument('--min-sleep-time', type=int, default=1,
                        help="Minimum time between checking for changes.")
    parser.add_argument('--no-setup', dest="setup", default=True,
                        action="store_false",
                        help="Skip system setup. Assume database content "
                        "matches hypervisor")
    parser.add_argument('--cfg', default=testpool.settings.CFG_FILE,
                        help="Override default configuration location "
                        "/etc/testpool/testpool.yml")
    return parser


def adapt(exts):
    """ Check to see if the pools should change. """

    LOGGER.info("adapt started")

    for profile1 in models.Profile.objects.all():

        if PROFILE_LOGGER:
            PROFILE_LOGGER.info(profile=profile1.name,
                                vm_count=profile1.vm_available(),
                                vm_max=profile1.vm_max)
        ext1 = exts[profile1.hv.product]
        vmpool = ext1.vmpool_get(profile1)
        algo.adapt(vmpool, profile1)

    LOGGER.info("adapt ended")


def action_destroy(exts, vmh):
    """ Reclaim any VMs released. """

    LOGGER.info("%s: action_destroy started %s %s",
                vmh.profile.name, vmh.profile.hv.product, vmh.name)

    ext1 = exts[vmh.profile.hv.product]
    vmpool = ext1.vmpool_get(vmh.profile)

    try:
        profile1 = vmh.profile
        algo.vm_destroy(vmpool, vmh)
        algo.adapt(vmpool, profile1)

        ##
        # If all of the VMs have been removed and the max is zero then
        # remove the VM.
        if profile1.deleteable():
            LOGGER.info("%s: action_destroy profile deleted",
                        vmh.profile.name)
            profile1.delete()
        ##
        LOGGER.info("%s: action_destroy %s done", profile1.name, vmh.name)
    except Exception, arg:
        LOGGER.debug("%s: action_destroy %s interrupted", profile1.name,
                     vmh.name)
        LOGGER.exception(arg)
        delta = vmpool.timing_get(api.VMPool.TIMING_REQUEST_DESTROY)
        vmh.transition(vmh.status, vmh.action, delta)


def action_clone(exts, vmh):
    """ Clone a new VM. """

    LOGGER.info("%s: action_clone started %s %s",
                vmh.profile.name, vmh.profile.hv.product, vmh.name)

    ext1 = exts[vmh.profile.hv.product]
    vmpool = ext1.vmpool_get(vmh.profile)
    try:
        algo.vm_clone(vmpool, vmh)
        algo.adapt(vmpool, vmh.profile)
        adapt(exts)
    except Exception:
        LOGGER.exception("%s: action_clone %s interrupted", vmh.profile.name,
                         vmh.name)
        delta = vmpool.timing_get(api.VMPool.TIMING_REQUEST_DESTROY)
        vmh.transition(vmh.status, vmh.action, delta)

    LOGGER.info("%s: action_clone done", vmh.profile.name)


def setup(exts):
    """ Run the setup of each hypervisor.

    VMs are reset to pending with the action to destroy them. Setup
    should be called only once before the event loop.
    """

    LOGGER.info("setup started")

    for profile1 in models.Profile.objects.all():
        vms = profile1.vm_set.all()
        LOGGER.info("setup %s %s %d of %d", profile1.name,
                    profile1.template_name, vms.count(), profile1.vm_max)

        ##
        # Check the hypervisor. Create Database entries for each existing
        # VM. Then mark them to be destroyed. Before that mark any
        # VMs in the database as BAD so that they can be deleted if they
        # do not correspond to an actual VM. Actual VMS, will be destroyed
        # through the normal event engine.
        for count in range(profile1.vm_max):
            vm_name = algo.vm_name_create(profile1.template_name, count)
            (vmh, _) = models.VM.objects.get_or_create(profile=profile1,
                                                       name=vm_name)
            # Mark bad just to figure out which to delete immediately.
            vmh.status = models.VM.BAD
            vmh.save()

        ##
        # Quickly go through all of the VMs to reclaim them by transitioning.
        # them to PENDING and action destroy
        ext1 = exts[profile1.hv.product]
        vmpool = ext1.vmpool_get(profile1)
        delta = 0
        vm_list = vmpool.vm_list(profile1)
        for vm_name in vm_list:
            try:
                vmh = models.VM.objects.get(profile=profile1, name=vm_name)
                vmh.transition(models.VM.PENDING, algo.ACTION_DESTROY, delta)
                LOGGER.info("setup mark VM %s to be destroyed", vmh.name)
                delta += vmpool.timing_get(api.VMPool.TIMING_REQUEST_DESTROY)
            except models.VM.DoesNotExist:
                pass

        for vmh in profile1.vm_set.filter(status=models.VM.BAD):
            LOGGER.info("setup deleted VM data %s", vmh.name)
            vmh.delete()
        ##

        ##
        # If the profile is already empty then delete the profile.
        if profile1.deleteable():
            LOGGER.info("%s: deleting profile", profile1.name)
            profile1.delete()
        ##

    LOGGER.info("setup ended")


def action_attr(exts, vmh):
    """ Retrieve attributes. """

    LOGGER.info("%s: action_attr started %s %s",
                vmh.profile.name, vmh.profile.hv.product, vmh.name)

    ##
    #  If VM expires reclaim it.
    ext1 = exts[vmh.profile.hv.product]
    vmpool = ext1.vmpool_get(vmh.profile)
    vmh.ip_addr = vmpool.ip_get(vmh.name)
    if vmh.ip_addr:
        LOGGER.info("%s: VM %s ip %s", vmh.profile.name, vmh.name,
                    vmh.ip_addr)
        vmh.transition(models.VM.READY, algo.ACTION_NONE, 1)
        adapt(exts)
    else:
        LOGGER.info("%s: VM %s waiting for ip addr", vmh.profile.name,
                    vmh.name)
        vmh.transition(vmh.status, vmh.action, 60)
    ##
    LOGGER.info("%s: action_attr ended", vmh.profile.name)


def mode_test_stop(args):
    """ Check to see if when in test mode to stop running. """

    if args.count == FOREVER:
        return False

    for vmh in models.VM.objects.all().order_by("action_time"):
        action_delay = vmh.action_time - datetime.datetime.now()
        action_delay = action_delay.seconds

        if models.VM.status_to_str(vmh.status) != "ready":
            return False

    return True


def events_show(banner):
    """ Show all of the pending events. """

    for vmh in models.VM.objects.all().order_by("action_time"):
        action_delay = vmh.action_time - datetime.datetime.now()
        action_delay = action_delay.seconds

        LOGGER.info("%s: %s %s action %s at %s", vmh.name, banner,
                    models.VM.status_to_str(vmh.status), vmh.action,
                    vmh.action_time.strftime("%Y-%m-%d %H:%M:%S"))


def action_vm(vmh):
    """ Handle VM actions.
    A VM can be destroyed, cloned or its IP address determined.
    """

    exts = ext.api_ext_list()
    LOGGER.info("%s: status %s action %s at %s", vmh.name,
                models.VM.status_to_str(vmh.status), vmh.action,
                vmh.action_time.strftime("%Y-%m-%d %H:%M:%S"))

    if vmh.action == algo.ACTION_DESTROY:
        action_destroy(exts, vmh)
    elif vmh.action == algo.ACTION_CLONE:
        action_clone(exts, vmh)
    elif vmh.action == algo.ACTION_ATTR:
        action_attr(exts, vmh)
    elif vmh.action == algo.ACTION_NONE:
        pass


def main(args):
    """ Main entry point for server. """

    count = args.count

    LOGGER.info("testpool server started")
    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    ##
    # Restart the daemon if extensions change.
    exts = ext.api_ext_list()
    if args.setup:
        exceptions.try_catch(coding.Curry(setup, exts))
    else:
        LOGGER.info("testpool server setup skipped")
    exceptions.try_catch(coding.Curry(adapt, exts))
    ##

    while count == FOREVER or count > 0:
        events_show("VMs")
        if mode_test_stop(args):
            return 0

        current = datetime.datetime.now()
        vmh = models.VM.objects.exclude(
            status=models.VM.READY).order_by("action_time").first()

        if not vmh:
            LOGGER.info("testpool no actions sleeping %s (seconds)",
                        args.max_sleep_time)
            time.sleep(args.max_sleep_time)
        elif vmh.action_time < current or args.max_sleep_time == 0:
            exceptions.try_catch(coding.Curry(action_vm, vmh))
        else:
            action_delay = abs(vmh.action_time - current).seconds

            sleep_time = min(args.max_sleep_time, action_delay)
            sleep_time = max(args.min_sleep_time, sleep_time)

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
        self.count = 100
        self.sleep_time = 0
        self.max_sleep_time = 0
        self.min_sleep_time = 0
        self.setup = True
        self.verbose = 2


class ModelTestCase(unittest.TestCase):
    """ Test model output. """

    profile_name = "test.server.profile"

    @staticmethod
    def fake_args():
        """ Return fake args to pass to main. """
        return FakeArgs()

    def test_setup(self):
        """ test_setup. """

        (hv1, _) = models.HV.objects.get_or_create(connection="localhost",
                                                   product="fake")

        defaults = {"vm_max": 1, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        profile1.delete()

    def tearDown(self):
        profile.profile_remove("test.server.profile", True)
        if os.path.exists("/tmp/testpool/fake/localhost/test.server.profile"):
            os.remove("/tmp/testpool/fake/localhost/test.server.profile")

    def test_shrink(self):
        """ test_shrink. """

        product = "fake"
        connection = "localhost"

        (hv1, _) = models.HV.objects.get_or_create(connection=connection,
                                                   product=product)
        defaults = {"vm_max": 10, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, hv=hv1, defaults=defaults)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()
        ##

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        exts = testpool.core.ext.api_ext_list()

        vmpool = exts[product].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list(profile1)), 2)

    def test_expand(self):
        """ test_expand. """

        product = "fake"
        connection = "localhost"

        (hv1, _) = models.HV.objects.get_or_create(connection=connection,
                                                   product=product)
        defaults = {"vm_max": 3, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, hv=hv1, defaults=defaults)

        ##
        # Now expand to 12
        profile1.vm_max = 12
        profile1.save()
        ##

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

        exts = testpool.core.ext.api_ext_list()
        vmpool = exts[product].vmpool_get(profile1)
        self.assertEqual(len(vmpool.vm_list(profile1)), 12)

    def test_expiration(self):
        """ test_expiration. """

        product = "fake"
        connection = "localhost"
        vm_max = 3

        (hv1, _) = models.HV.objects.get_or_create(connection=connection,
                                                   product=product)
        defaults = {"vm_max": vm_max, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

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
        self.assertEqual(main(args), 0)
        ##

        exts = testpool.core.ext.api_ext_list()
        adapt(exts)

        vms = profile1.vm_set.filter(status=models.VM.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(vms.count(), 2)
        ##

    def test_profile_log(self):
        """ test structure log format. """

        logger = profile_log_create("./profile.log")
        self.assertTrue(logger)
        logger.info(profile="example", vm_count=1, vm_max=2)
