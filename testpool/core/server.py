""" Test pool Server. """
import logging
import unittest
import time
import testpool.core.ext
import testpool.core.algo
from testpooldb import models

FOREVER = None


def reclaim(api_exts):
    """ Reclaim any VMs released. """

    logging.info("testpool reclaim started")

    for vm1 in models.VM.objects.filter(status=models.VM.RELEASED):
        logging.info("loading %s %s", vm1.profile.hv.product,
                     vm1.profile.hv.hostname)
        api_ext = api_exts[vm1.profile.hv.product]
        vm_pool = api_ext.vmpool_get(vm1.profile.hv.hostname)
        testpool.core.algo.reclaim(vm_pool, vm1)
    logging.info("testpool reclaim ended")


def setup(api_exts):
    """ Run the setup of each hypervisor. """

    logging.info("testpool setup started")
    for profile in models.Profile.objects.all():
        logging.info("setup %s %s %s", profile.name, profile.template_name,
                     profile.vm_max)
        api_ext = api_exts[profile.hv.product]
        testpool.core.algo.setup(api_ext, profile.name, profile.template_name,
                                 profile.vm_max)
    logging.info("testpool setup ended")


def main(count=FOREVER, sleep_time=60):
    """ Main entry point for server. """

    logging.info("testpool server started")

    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    api_exts = testpool.core.ext.ext_list()
    setup(api_exts)

    while count == FOREVER or count > 0:
        api_exts = testpool.core.ext.ext_list()
        testpool.core.server.reclaim(api_exts)
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
        (profile1, _) = models.Profile.objects.get_or_create(
            name="fake.profile.1", hv=hv1, template_name="fake.template",
            vm_max=10)

        logging.basicConfig(level=logging.DEBUG)
        self.assertEqual(main(1, 1), 0)
