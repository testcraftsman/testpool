# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testpool
#
# Testbed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Testbed is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Testdb.  If not, see <http://www.gnu.org/licenses/>.
"""
Fake profiles used for development.

This profile pretends to manage a pool of VMs which are merely pretend
VMS which do not exist.
"""
import logging
from testpooldb import models


def vm_remove(hostname, product, profile, vm_name):
    """ Remove a vm. """

    try:
        hv1 = models.HV.objects.get(hostname=hostname, product=product)
        profile1 = models.Profile.objects.get(name=profile, hv=hv1)

        vm1 = models.VM.objects.get(profile=profile1, name=vm_name)
        vm1.delete()

    except models.HV.DoesNotExist:
        return 0
    except models.Profile.DoesNotExist:
        profiles = models.Profile.objects.filter(hv=hv1)
        if profiles.count() == 0:
            hv1.delete()
        return 0
    except models.VM.DoesNotExist:
        profile1.delete()
        return 0

    vms = models.Profile.objects.filter(hv=hv1)
    if vms.count() == 0:
        hv1.delete()


def vm_add(hostname, product, vm_name, vm_max, template_name):
    """ Add a vm. """

    (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                               product=product)
    defaults = {"vm_max": vm_max, "template_name": template_name}
    models.Profile.objects.update_or_create(name=vm_name, hv=hv1,
                                            defaults=defaults)


def _do_vm_remove(args):
    """ Remove a vm. """

    logging.info("remove a vm %s", args.vm)
    vm_remove(args.hostname, args.product, args.profile, args.vm)


def _do_vm_add(args):
    """ Add or modify an vm.

    If the fake vm exists, calling this again will change the
    maximum number of VMS and the template name.
    """

    logging.info("add a vm %s", args.vm)
    vm_add(args.hostname, args.product, args.vm, args.max,
           args.template_name)


def _do_vm_list(args):
    """ List all vms. """

    fmt = "%-16s %-8s %-20s %s"

    logging.info("list vms")
    hv1 = models.HV.objects.get(hostname=args.hostname, product=args.product)
    profile1 = models.Profile.objects.get(hv=hv1, name=args.profile)
    vms = models.VM.objects.filter(profile=profile1)

    print fmt % ("Name", "Status", "Reserved", "Expiration")
    for vm1 in vms.order_by("id"):
        print fmt % (vm1.name, models.VM.status_to_str(vm1.status),
                     vm1.reserved, vm1.expiration)


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("vm",
                                  help="Commands to manage fake vms",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Add
    parser = rootparser.add_parser("add", description=_do_vm_add.__doc__,
                                   help="Add a vm")
    parser.set_defaults(func=_do_vm_add)
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    ##

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_vm_list.__doc__,
                                   help="List vms")
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.set_defaults(func=_do_vm_list)
    ##

    ##
    # Remove
    parser = rootparser.add_parser("remove",
                                   description=_do_vm_remove.__doc__,
                                   help="Remove a vm")
    parser.set_defaults(func=_do_vm_remove)
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("profile", type=str, help="The name of the profile.")
    parser.add_argument("vm", type=str, help="Name of the fake vm.")
    ##

    return subparser
