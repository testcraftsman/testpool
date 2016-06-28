""" Test pool Server. """
import logging
import unittest
import time
import testpool.core.ext
import testpool.core.algo
from testpooldb import models

FOREVER = None


def reclaim(exts):
    """ Reclaim any VMs released. """

    logging.info("testpool reclaim started")

    for vm1 in models.VM.objects.filter(status=models.VM.RELEASED):
        logging.info("loading %s %s", vm1.profile.hv.product,
                     vm1.profile.hv.hostname)
        ext = exts[vm1.profile.hv.product]
        testpool.core.algo.reclaim(ext, vm1)
    logging.info("testpool reclaim ended")


def setup(exts):
    """ Run the setup of each hypervisor. """

    logging.info("testpool setup started")
    for profile in models.Profile.objects.all():
        logging.info("setup %s %s %s", profile.name, profile.template_name,
                     profile.vm_max)
        ext = exts[profile.hv.product]
        testpool.core.algo.setup(ext, profile)
    logging.info("testpool setup ended")


def main(count=FOREVER, sleep_time=60):
    """ Main entry point for server. """

    logging.info("testpool server started")

    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    ##
    # Restart the daemon if extensions change.
    exts = testpool.core.ext.ext_list()
    #
    setup(exts)

    while count == FOREVER or count > 0:
        testpool.core.server.reclaim(exts)
        time.sleep(sleep_time)

        if count != FOREVER:
            count -= 1

    logging.info("testpool server stopped")
    return 0


class ModelTestCase(unittest.TestCase):
    """ Test model output. """

    def test_setup(self):
        """ test_setup. """

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product="fake")

        defaults = {"vm_max": 1, "template_name": "fake.template"}
        models.Profile.objects.update_or_create(name="fake.profile.1",
                                                hv=hv1, defaults=defaults)

        logging1 = logging.getLogger("django.db.backends")
        logging1.setLevel(logging.WARNING)

        logging1 = logging.getLogger(None)
        logging1.setLevel(logging.DEBUG)
        self.assertEqual(main(1, 1), 0)
