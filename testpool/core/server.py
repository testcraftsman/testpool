import testpool.core.algo

def reclaim(api_exts):
    """ Reclaim any VMs released. """

    logging.info("reclaiming used VMs.")

    for vm in models.VM.objects.filter(status=models.VM.RELEASED):
        logging.debug("loading %s %s", vm.profile.hv.product,
                      vm.profile.hv.hostname)
        api_ext = api_exts[vm.profile.hv.product]
        api_ext.vmpool_get(vm.profile.hv.hostname)
        testpool.core.algo.reclaim(api_ext, vm)

