""" Test pool Server. """
import logging
import unittest
import time
import testpool.core.ext
import testpool.core.algo
from testpool.core import commands
from testpool.core import profile
from testpooldb import models

FOREVER = None


def argparser():
    """Create server arg parser. """

    parser = commands.argparser()
    parser.add_argument('--count', type=int, default=FOREVER)
    parser.add_argument('--sleep-time', type=int, default=60,
                        help="Time between checking for changes.")

    return parser


def adapt(exts):
    """ Check to see if the pools should change. """

    for profile1 in models.Profile.objects.all():
        ext = exts[profile1.hv.product]
        vmpool = ext.vmpool_get(profile1.hv.hostname)
        testpool.core.algo.adapt(vmpool, profile1)


def reclaim(exts):
    """ Reclaim any VMs released. """

    logging.info("testpool reclaim started")

    for vm1 in models.VM.objects.filter(status=models.VM.RELEASED):
        logging.info("loading %s %s", vm1.profile.hv.product,
                     vm1.profile.hv.hostname)
        ext = exts[vm1.profile.hv.product]
        vmpool = ext.vmpool_get(vm1.profile.hv.hostname)

        testpool.core.algo.reclaim(vmpool, vm1)
    logging.info("testpool reclaim ended")


def setup(exts):
    """ Run the setup of each hypervisor. """

    logging.info("testpool setup started")
    for profile1 in models.Profile.objects.all():
        logging.info("setup %s %s %s", profile1.name, profile1.template_name,
                     profile1.vm_max)
        ext = exts[profile1.hv.product]
        vmpool = ext.vmpool_get(profile1.hv.hostname)
        logging.info("algo.setup %s %s", profile1.name, profile1.template_name)
        logging.info("algo.setup HV %s %d VMs", profile1.hv, profile1.vm_max)

        testpool.core.algo.remove(vmpool, profile1)
    logging.info("testpool setup ended")


def main(args):
    """ Main entry point for server. """

    count = args.count

    logging.info("testpool server started")
    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    ##
    # Restart the daemon if extensions change.
    exts = testpool.core.ext.ext_list()
    #
    setup(exts)

    while count == FOREVER or count > 0:
        adapt(exts)
        reclaim(exts)
        if args.sleep_time > 0:
            time.sleep(args.sleep_time)

        if count != FOREVER:
            count -= 1

    logging.info("testpool server stopped")
    return 0


class ModelTestCase(unittest.TestCase):
    """ Test model output. """

    @staticmethod
    def fake_args():
        """ Return fake args to pass to main. """
        parser = argparser()
        args = parser.parse_args()
        args.count = 1
        args.sleep_time = 0

        return args

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

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product=product)
        defaults = {"vm_max": 10, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="fake.profile.2", hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)
        exts = testpool.core.ext.ext_list()

        vmpool = exts[product].vmpool_get("localhost")

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()

        adapt(exts)

        vmpool = exts[product].vmpool_get("localhost")
        self.assertEqual(len(vmpool.vm_list()), 2)

    def test_expand(self):
        """ test_expand. """

        product = "fake"

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product=product)
        defaults = {"vm_max": 3, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="fake.profile.2", hv=hv1, defaults=defaults)

        args = ModelTestCase.fake_args()
        self.assertEqual(main(args), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 12
        profile1.save()

        exts = testpool.core.ext.ext_list()
        adapt(exts)

        vmpool = exts[product].vmpool_get("localhost")
        self.assertEqual(len(vmpool.vm_list()), 12)


if __name__ == "__main__":
    unittest.main()
