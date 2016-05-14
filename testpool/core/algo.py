import unittest
from testpool.db.testpool import models
"""
   Algorithm for modifying database.
"""
def setup(intf, hostname, profile_name, template_name, vm_max):

    hv1 = models.HV.objects.create(hostname=hostname, product=intf.type_get())
    profile1 = models.Profile.objects.create(hv=hv1, name=profile_name,
                                             template_name=template_name,
                                             vm_max=vm_max)

    for count in range(vm_max):
        vm_name = template_name + ".%d" % count
        intf.clone(template_name, vm_name)
        intf.start(vm_name)
        models.VM.objects.create(profile=profile1, name=vm_name,
                                 status=models.VM.FREE)

    return 0

