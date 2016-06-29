""" Test pool Server. """
import logging
import unittest
import time
import testpool.core.ext
import testpool.core.algo
from testpooldb import models

FOREVER = None


def adapt(exts):
    """ Check to see if the pools should change. """

    for profile in models.Profile.objects.all():
        ext = exts[profile.hv.product]
        vmpool = ext.vmpool_get(profile.hv.hostname)
        testpool.core.algo.adapt(vmpool, profile)


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
    for profile in models.Profile.objects.all():
        logging.info("setup %s %s %s", profile.name, profile.template_name,
                     profile.vm_max)
        ext = exts[profile.hv.product]
        vmpool = ext.vmpool_get(profile.hv.hostname)
        logging.info("algo.setup %s %s", profile.name, profile.template_name)
        logging.info("algo.setup HV %s %d VMs", profile.hv, profile.vm_max)

        testpool.core.algo.remove(vmpool, profile)
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
        adapt(exts)
        reclaim(exts)
        if sleep_time > 0:
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

        self.assertEqual(main(1, 0), 0)

    def test_shrink(self):
        """ test_shrink. """

        product = "fake"

        (hv1, _) = models.HV.objects.get_or_create(hostname="localhost",
                                                   product=product)
        defaults = {"vm_max": 10, "template_name": "fake.template"}
        (profile1, _) = models.Profile.objects.update_or_create(
            name="fake.profile.2", hv=hv1, defaults=defaults)

        self.assertEqual(main(1, 0), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 2
        profile1.save()

        exts = testpool.core.ext.ext_list()
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

        self.assertEqual(main(1, 0), 0)

        ##
        # Now shrink the pool to two
        profile1.vm_max = 12
        profile1.save()

        exts = testpool.core.ext.ext_list()
        adapt(exts)

        vmpool = exts[product].vmpool_get("localhost")
        self.assertEqual(len(vmpool.vm_list()), 12)
