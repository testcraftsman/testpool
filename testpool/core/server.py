import logging
import testpool.core.algo
from testpool.db.testpool import models
from django.test import TestCase

FOREVER = None

def reclaim(api_exts):
    """ Reclaim any VMs released. """

    for vm in models.VM.objects.filter(status=models.VM.RELEASED):
        logging.info("loading %s %s", vm.profile.hv.product,
                     vm.profile.hv.hostname)
        api_ext = api_exts[vm.profile.hv.product]
        vm_pool = api_ext.vmpool_get(vm.profile.hv.hostname)
        testpool.core.algo.reclaim(vm_pool, vm)

def setup(api_exts):
    """ Run the setup of each hypervisor. """

    logging.info("testpool setup")
    for vmpool in models.Profile.objects.all():
        logging.info("setup %s %s %s %s", vmpool, profile.name,
                     profile.template_name, profile.vm_max)
        rtc = testpool.core.algo.setup(vmpool, profile.name,
                                       profile.template_name,
                                       profile.vm_max)

def main(count=FOREVER):
    """ Main entry point for server. """

    if count != FOREVER and count < 0:
        raise ValueError("count should be a positive number or FOREVER")

    api_exts = testpool.core.ext.ext_list()
    setup(api_exts)

    while count == FOREVER or count > 0:
        api_exts = testpool.core.ext.ext_list()
        testpool.core.server.reclaim(api_exts)
        time.sleep(60)

        if count != FOREVER:
            count -= 1

class ModelTestCase(TestCase):
    """ Test model output. """

    def test_setup(self):
        """ test_setup. """
        print "MARK: 1"
