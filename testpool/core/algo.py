import unittest
import logging
from testpool.db.testpool import models
import testpool.core.api

"""
   Algorithm for modifying database.
"""
def setup(intf, hostname, profile_name, template_name, vm_max):

    logging.info("setup %s %s %s %s", intf, hostname, profile_name,
                 template_name)

    (hv1, gcr) = models.HV.objects.get_or_create(hostname=hostname,
                                                 product=intf.type_get())
    logging.debug("setup HV %s %d", hv1, gcr)
    (profile1, gcr) = models.Profile.objects.get_or_create(
        hv=hv1, name=profile_name, template_name=template_name, vm_max=vm_max)
    logging.debug("setup Profile %s %d", profile1, gcr)

    for count in range(vm_max):
        vm_name = template_name + ".%d" % count
        logging.debug("setup %s VM %s", profile1, vm_name)
        (vm1, gcr) = models.VM.objects.get_or_create(profile=profile1,
                                                     name=vm_name,
                                                     status=models.VM.FREE)
        vm_state = intf.vm_state_get(vm_name)
        logging.debug("setup %s VM %s state %d", profile1, vm1, vm_state)
        if vm_state != testpool.core.api.VMPool.STATE_NONE:
            intf.destroy(vm_name)
            
        intf.clone(template_name, vm_name)
        vm_state = intf.start(vm_name)
        logging.debug("setup %s VM cloned %s %d", profile1, vm1, vm_state)
        if vm_state != testpool.core.api.VMPool.STATE_RUNNING:
            logging.error("setup %s VM %s failed to start", profile1, vm1)
            intf.profile_mark_bad(profile_name)

    profile1.delete()
    hv1.delete()

    return 0
