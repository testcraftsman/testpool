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

Server algorithm. resources, given a current state, can be assigned an action
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
    # code really expects RFC3339Nano which is a version of iso8601.
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
    CFG = cfgcheck.check(args.cfg_file)
    if CFG:
        LOGGER.info("loading configuration file %s", args.cfg_file)
    else:
        LOGGER.warning("configuration file %s not found", args.cfg_file)
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
    parser.add_argument('--max-sleep-time', type=int, default=10,
                        help="Maximum time between checking for changes.")
    parser.add_argument('--min-sleep-time', type=int, default=1,
                        help="Minimum time between checking for changes.")
    parser.add_argument('--no-setup', dest="setup", default=True,
                        action="store_false",
                        help="Skip system setup. Assume database content "
                        "matches hypervisor")
    parser.add_argument('--cfg-file', dest="cfg_file",
                        default=testpool.settings.CFG_FILE,
                        help="Override default configuration location "
                        "/etc/testpool/testpool.yml")
    return parser


def adapt(exts):
    """ Check to see if the pools should change. """

    LOGGER.info("adapt started")

    for profile1 in models.Profile.objects.all():

        if PROFILE_LOGGER:
            PROFILE_LOGGER.info(profile=profile1.name,
                                resource_count=profile1.resource_available(),
                                resource_max=profile1.resource_max)
        ext1 = exts[profile1.host.product]
        pool = ext1.pool_get(profile1)
        algo.adapt(pool, profile1)

    LOGGER.info("adapt ended")


def action_destroy(exts, rsrc):
    """ Reclaim any resources released. """

    try:
        rsrc_name = rsrc.name
        LOGGER.info("%s: action_destroy started %s %s",
                    rsrc.profile.name, rsrc.profile.host.product, rsrc.name)

        ext1 = exts[rsrc.profile.host.product]
        pool = ext1.pool_get(rsrc.profile)

        profile1 = rsrc.profile

        algo.resource_destroy(pool, rsrc)

        ##
        # If all of the resources have been removed and the max is zero then
        # remove the resource.
        if profile1.deleteable():
            profile1.delete()
            LOGGER.info("%s: action_destroy profile deleted", profile1.name)
        else:
            algo.adapt(pool, profile1)
        ##
        LOGGER.info("%s: action_destroy %s done", profile1.name, rsrc_name)
    except Exception, arg:
        LOGGER.debug("action_destroy %s interrupted", rsrc_name)
        LOGGER.exception(arg)
        delta = pool.timing_get(api.Pool.TIMING_REQUEST_DESTROY)
        rsrc.transition(rsrc.status, rsrc.action, delta)


def action_clone(exts, rsrc):
    """ Clone a new resource. """

    try:
        rsrc_name = rsrc.name
        LOGGER.info("%s: action_clone started %s %s",
                    rsrc.profile.name, rsrc.profile.host.product, rsrc.name)

        ext1 = exts[rsrc.profile.host.product]
        pool = ext1.pool_get(rsrc.profile)

        profile1 = rsrc.profile

        algo.resource_clone(pool, rsrc)

        algo.adapt(pool, rsrc.profile)
        LOGGER.info("%s: action_clone %s done", profile1.name, rsrc_name)
    except Exception:
        LOGGER.exception("action_clone %s interrupted", rsrc.name)
        delta = pool.timing_get(api.Pool.TIMING_REQUEST_DESTROY)
        rsrc.transition(rsrc.status, rsrc.action, delta)

    LOGGER.info("%s: action_clone done", rsrc.profile.name)


def setup(exts):
    """ Run the setup of each hypervisor.

    resources are reset to pending with the action to destroy them. Setup
    should be called only once before the event loop.
    """

    LOGGER.info("setup started")

    ##
    # Check for dangling items in the database. They are created when
    # the database crashes in the middle of changes across multiple
    # tables.
    # Delete profiles first in case we create dangling resources from it.
    for profile1 in models.Profile.objects.all():
        if profile1.deleteable():
            LOGGER.warning("deleting profile %s because max resource is 0",
                           profile1.name)
            profile1.delete()
            profile1.save()

    for profile1 in models.Profile.objects.filter(template_name__isnull=True):
        LOGGER.warning("deleting resource %s because template is unknown",
                       profile1.name)
        profile1.delete()
        profile1.save()

    for rsrc in models.Resource.objects.filter(profile__isnull=True):
        LOGGER.warning("deleting resource %s because profile is unknown",
                       rsrc.name)
        rsrc.delete()
        rsrc.save()

    ##

    for profile1 in models.Profile.objects.all():
        rsrcs = profile1.resource_set.all()
        LOGGER.info("setup %s %s %d of %d", profile1.name,
                    profile1.template_name, rsrcs.count(),
                    profile1.resource_max)

        ext1 = exts[profile1.host.product]
        pool = ext1.pool_get(profile1)

        ##
        # Check the hypervisor. Create Database entries for each existing
        # resource. Then mark them to be destroyed. Before that mark any
        # resources in the database as BAD so that they can be deleted if they
        # do not correspond to an actual resource. Actual resources, will be
        # destroyed through the normal event engine.
        for count in range(profile1.resource_max):
            name = pool.new_name_get(profile1.template_name, count)
            for rsrc in models.Resource.objects.filter(profile=profile1,
                                                       name=name):
                # Mark bad just to figure out which to delete immediately.
                rsrc.status = models.Resource.BAD
                rsrc.save()

        ##
        # Quickly go through all of the resources to reclaim them by
        # transitioning. them to PENDING and action destroy
        delta = 0
        names = pool.list(profile1)
        for name in names:
            try:
                for rsrc in models.Resource.objects.filter(profile=profile1,
                                                           name=name):
                    rsrc.transition(models.Resource.PENDING,
                                    algo.ACTION_DESTROY, delta)
                    LOGGER.info("setup mark resource %s to be destroyed",
                                rsrc.name)
                delta += pool.timing_get(api.Pool.TIMING_REQUEST_DESTROY)
            except models.Resource.DoesNotExist:
                pass

        for rsrc in profile1.resource_set.filter(status=models.Resource.BAD):
            LOGGER.info("setup deleted resource data %s", rsrc.name)
            rsrc.delete()
        ##

        ##
        # If the profile is already empty then delete the profile.
        if profile1.deleteable():
            LOGGER.info("%s: deleting profile", profile1.name)
            profile1.delete()
        ##

    LOGGER.info("setup ended")


def action_attr(exts, rsrc):
    """ Retrieve attributes. """

    LOGGER.info("%s: action_attr started %s %s",
                rsrc.profile.name, rsrc.profile.host.product, rsrc.name)

    ##
    #  If resource expires reclaim it.
    ext1 = exts[rsrc.profile.host.product]
    pool = ext1.pool_get(rsrc.profile)
    rsrc.ip_addr = pool.ip_get(rsrc.name)
    if rsrc.ip_addr:
        LOGGER.info("%s: resource %s ip %s", rsrc.profile.name, rsrc.name,
                    rsrc.ip_addr)
        delta = pool.timing_get(api.Pool.TIMING_REQUEST_NONE)
        rsrc.transition(models.Resource.READY, algo.ACTION_NONE, delta)
        algo.adapt(pool, rsrc.profile)
    else:
        LOGGER.info("%s: resource %s waiting for ip addr", rsrc.profile.name,
                    rsrc.name)
        rsrc.transition(rsrc.status, rsrc.action, 60)
    ##
    LOGGER.info("%s: action_attr ended", rsrc.profile.name)


def mode_test_stop(args):
    """ Check to see if when in test mode to stop running. """

    if args.count == FOREVER:
        return False

    for rsrc in models.Resource.objects.all().order_by("action_time"):
        action_delay = rsrc.action_time - datetime.datetime.now()
        action_delay = action_delay.seconds

        if models.Resource.status_to_str(rsrc.status) != "ready":
            return False

    return True


def events_show(banner):
    """ Show all of the pending events. """

    for rsrc in models.Resource.objects.all().order_by("action_time"):
        action_delay = rsrc.action_time - datetime.datetime.now()
        action_delay = action_delay.seconds

        try:
            LOGGER.debug("%s: %s.%s %s action %s at %s", banner,
                         rsrc.profile.name, rsrc.name,
                         models.Resource.status_to_str(rsrc.status),
                         rsrc.action,
                         rsrc.action_time.strftime("%Y-%m-%d %H:%M:%S"))
        except models.Profile.DoesNotExist:
            # If at any time resource becomes unattached to a profile
            # then delete the resource.
            rsrc.delete()


def action_resource(rsrc):
    """ Handle resource actions.

    A resource can be destroyed, cloned or its IP address determined.
    """

    exts = ext.api_ext_list()
    LOGGER.info("%s: status %s action %s at %s", rsrc.name,
                models.Resource.status_to_str(rsrc.status), rsrc.action,
                rsrc.action_time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        if rsrc.action == algo.ACTION_DESTROY:
            action_destroy(exts, rsrc)
        elif rsrc.action == algo.ACTION_CLONE:
            action_clone(exts, rsrc)
        elif rsrc.action == algo.ACTION_ATTR:
            action_attr(exts, rsrc)
        elif rsrc.action == algo.ACTION_NONE:
            pass
    except models.Profile.DoesNotExist:
        LOGGER.debug("action %s deleted because profile missing.", rsrc.name)
        rsrc.delete()


def main(args):
    """ Main entry point for server. """

    count = args.count

    LOGGER.info("testpool server started")
    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    ##
    # Restart the daemon if extensions change. Keep a handle to the extensions.
    # if the list of extensions changes, this daemon must be restarted to
    # retrive the new extensions.
    exts = ext.api_ext_list()
    if args.setup:
        exceptions.try_catch(coding.Curry(setup, exts))
    else:
        LOGGER.info("testpool server setup skipped")
    exceptions.try_catch(coding.Curry(adapt, exts))
    ##

    while count == FOREVER or count > 0:
        events_show("Resources")
        if mode_test_stop(args):
            return 0

        ##
        # Retrieve resources. For action items that are ready run the
        # required action.
        current = datetime.datetime.now()
        LOGGER.info("checking actions %s", current)
        rsrcs = models.Resource.objects.exclude(status=models.Resource.READY)
        rsrcs = rsrcs.order_by("action_time")

        if not rsrcs:
            LOGGER.info("testpool no actions sleeping %s (seconds)",
                        args.max_sleep_time)
            time.sleep(args.max_sleep_time)
            continue

        ##
        # Check the first action. If its not ready to fire then all
        # actions are not ready to fire. Calculate the amount of time
        # to sleep but take into consideration the minimum and maximum
        # sleep times as well.
        #
        # The maximum amount of sleep time should be reasonable so that
        # changes to the database will be detected in a reasonable amount
        # of time.
        rsrc = rsrcs.first()
        if rsrc.action_time > current and args.max_sleep_time != 0:
            action_delay = abs(rsrc.action_time - current).seconds

            sleep_time = min(args.max_sleep_time, action_delay)
            sleep_time = max(args.min_sleep_time, sleep_time)
            LOGGER.info("testpool sleeping %s (seconds)", sleep_time)
            time.sleep(sleep_time)
            continue

        LOGGER.info("testpool actions fired")
        for rsrc in rsrcs:
            if rsrc.action_time < current or args.max_sleep_time == 0:
                exceptions.try_catch(coding.Curry(action_resource, rsrc))
            else:
                break

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

    ##
    # Re-use this name in the tests to make it easy to clean up.
    profile_name = "test.server.profile"

    @staticmethod
    def fake_args():
        """ Return fake args to pass to main. """
        return FakeArgs()

    def test_setup(self):
        """ test_setup. """

        (host1, _) = models.Host.objects.get_or_create(connection="localhost",
                                                       product="fake")

        defaults = {"resource_max": 1, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, host=host1, defaults=defaults)

        self.assertTrue(profile1)
        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

    def tearDown(self):
        """ Remove any test resources. """

        try:
            algo.profile_remove(self.profile_name, True)
        except models.Profile.DoesNotExist:
            pass
        if os.path.exists("/tmp/testpool/fake/localhost/test.server.profile"):
            os.remove("/tmp/testpool/fake/localhost/test.server.profile")

    def test_shrink(self):
        """ test_shrink. """

        product = "fake"
        connection = "localhost"

        (host1, _) = models.Host.objects.get_or_create(connection=connection,
                                                       product=product)
        defaults = {"resource_max": 10, "template_name": "test.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, host=host1, defaults=defaults)

        ##
        # Now shrink the pool to two
        profile1.resource_max = 2
        profile1.save()
        ##

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        exts = testpool.core.ext.api_ext_list()

        pool = exts[product].pool_get(profile1)
        self.assertEqual(len(pool.list(profile1)), 2)

    def test_expand(self):
        """ test_expand. """

        product = "fake"
        connection = "localhost"

        (host1, _) = models.Host.objects.get_or_create(connection=connection,
                                                       product=product)
        defaults = {"resource_max": 3, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, host=host1, defaults=defaults)

        ##
        # Now expand to 12
        profile1.resource_max = 12
        profile1.save()
        ##

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

        exts = testpool.core.ext.api_ext_list()
        pool = exts[product].pool_get(profile1)
        self.assertEqual(len(pool.list(profile1)), 12)

    def test_expiration(self):
        """ test_expiration. """

        product = "fake"
        connection = "localhost"
        resource_max = 3

        ##
        # Create three resources.
        (host1, _) = models.Host.objects.get_or_create(connection=connection,
                                                       product=product)
        defaults = {
            "resource_max": resource_max,
            "template_name": "test.template"
        }
        (profile1, _) = models.Profile.objects.update_or_create(
            name=self.profile_name, host=host1, defaults=defaults)

        args = ModelTestCase.fake_args()
        # Run the main so that the state-machine runs to build the three
        # resources.
        self.assertEqual(main(args), 0)
        rsrcs = profile1.resource_set.filter(status=models.Resource.READY)
        self.assertEqual(len(rsrcs), resource_max)
        ##

        ##
        # Pick a resource and mark it ready to be destroyed.

        rsrc = rsrcs[0]
        rsrc.transition(models.Resource.RESERVED, algo.ACTION_DESTROY, 1)

        ##
        time.sleep(2)
        args.setup = False
        args.count = 2
        args.sleep_time = 1
        args.max_sleep_time = 1
        args.min_sleep_time = 1
        self.assertEqual(main(args), 0)
        ##

        exts = testpool.core.ext.api_ext_list()
        adapt(exts)

        rsrcs = profile1.resource_set.filter(status=models.Resource.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(rsrcs.count(), 2)
        ##

    def test_profile_log(self):
        """ test structure log format. """

        logger1 = profile_log_create("./profile.log")
        self.assertTrue(logger1)
        logger1.info(profile="example", resource_count=1, resource_max=2)
