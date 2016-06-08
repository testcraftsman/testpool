import logging
import testpool.core.algo
from testpool.db.testpool import models

def reclaim(api_exts):
    """ Reclaim any VMs released. """

    logging.info("reclaiming used VMs.")

    for vm in models.VM.objects.filter(status=models.VM.RELEASED):
        print "MARK: vm", vm.name
        logging.debug("loading %s %s", vm.profile.hv.product,
                      vm.profile.hv.hostname)
        api_ext = api_exts[vm.profile.hv.product]
        print "MARK: api", api_ext
        vm_pool = api_ext.vmpool_get(vm.profile.hv.hostname)

        testpool.core.algo.reclaim(vm_pool, vm)