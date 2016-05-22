import unittest
import logging
from testpool.db.testpool import models
import testpool.core.api


class NoResources(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def onerror(name):
    """ Show module that fails to load. """
    LOGGER.error("importing module %s", name)
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)


def intf_find():
    """ Look for command intf. """

    for package in testpool.settings.PLUGINS:
        LOGGER.debug("loading commands %s", package)

        package = importlib.import_module(package)
        for _, module, ispkg in pkgutil.walk_packages(package.__path__,
                                                      package.__name__ + ".",
                                                      onerror=onerror):
            ##
            # only include commands from commands.py files.
            if ispkg or not module.endswith("commands"):
                continue
            LOGGER.debug("  loading commands from %s", module)
            module = importlib.import_module(module)
            try:
                module.add_subparser(subparser)
            except AttributeError, arg:
                ##
                # This means that the module is missing the add method.
                # All modules identified in settings to extend CLI
                # must have an add method
                LOGGER.error("adding subparser for %s.%s", package, module)
                LOGGER.exception(arg)


def main():
    """ Entry point for parsing tbd arguments. """


"""
   Algorithm for modifying database.
"""
def setup(intf, profile_name, template_name, vm_max):

    logging.info("setup %s %s %s %s", intf, profile_name, template_name)

    ##
    # \todo hostname should change to context
    (hv1, gcr) = models.HV.objects.get_or_create(hostname=intf.context,
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

    return 0

def pop(profile_name):
    logging.info("pop VM from %s", profile_name)

    profile1 = models.Profile.objects.get(name=profile_name)

    try:
        vm1 = models.VM.objects.filter(profile=profile1, status=models.VM.FREE)[0]
        vm1.status=models.VM.RESERVED
        vm1.save()
    except IndexError:
        raise NoResources("%s: all VMs taken" % profile_name)

    return vm1

def push(vm_id):

    logging.info("push %d", vm_id)

    vm1 = models.VM.objects.get(id=vm_id, status=models.VM.RELEASED)
    vm1.save()

    return 0

def reclaim():

    for vm in models.VM.objects.filter(status=models.VM.RELEASED):
        profile1 = models.Profile.objects.get_or_create(name=profile_name)
        print "MARK:", vm.profile, profile1.hv1.product
