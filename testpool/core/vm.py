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
from django.db.models import Q
from testpooldb import models


def _profile_get(hostname, product, profile):
    """ Return the profile given the parameters. """
    hv1 = models.HV.objects.get(hostname=hostname, product=product)
    return models.Profile.objects.get(name=profile, hv=hv1)


def _do_vm_incr(args):
    """ Increment or decrement the number number of VMs. """

    logging.info("incrementing VMs %s %s %s %d", args.hostname, args.product,
                 args.profile, args.count)
    profile1 = _profile_get(args.hostname, args.product, args.profile)
    profile1.vm_max += args.count
    profile1.save()

    return 0


def _do_vm_release(args):
    """ Release VM. """

    logging.info("release %s %s %s", args.hostname, args.profile, args.vmname)
    vm1 = models.VM.objects.get(name=args.vmname,
                                profile__hv__hostname=args.hostname,
                                profile__name=args.profile)
    vm1.status = models.VM.RELEASED
    vm1.save()
    return 0


def _do_vm_reserve(args):
    """ Reserve VM. """

    logging.info("reserve %s %s %s", args.hostname, args.profile, args.vmname)
    vm1 = models.VM.objects.get(name=args.vmname,
                                profile__hv__hostname=args.hostname,
                                profile__name=args.profile)
    vm1.status = models.VM.RESERVED
    vm1.save()
    return 0


def _do_vm_list(args):
    """ List all vms. """

    fmt = "%-13s %-13s %-16s %-8s %-15s %s"

    logging.info("list vms by %s", args.patterns)
    vms = models.VM.objects.all()
    for pattern in args.patterns:
        vms = vms.filter(
            Q(name__contains=pattern) |
            Q(profile__hv__hostname__contains=pattern) |
            Q(profile__hv__product__contains=pattern) |
            Q(profile__name__contains=pattern)).order_by("name")

    print fmt % ("Host Name", "Profile", "Name", "Status", "Reserved",
                 "Expiration")
    for vm1 in vms:
        print fmt % (vm1.profile.hv.hostname, vm1.profile.name, vm1.name,
                     models.VM.status_to_str(vm1.status), vm1.reserved,
                     vm1.expiration)

    return 0


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("vm",
                                  help="Commands to manage fake vms",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Increment
    parser = rootparser.add_parser("incr", description=_do_vm_incr.__doc__,
                                   help="Increment the number of VMs")
    parser.set_defaults(func=_do_vm_incr)
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.add_argument("count", type=int,
                        help="Increment/decrement the maximum number of VMs.")
    ##

    parser = rootparser.add_parser("release", description=_do_vm_incr.__doc__,
                                   help="Release VM to be reclaimed.")
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.add_argument("vmname", type=str, help="The VM name.")
    parser.set_defaults(func=_do_vm_release)

    parser = rootparser.add_parser("reserve", description=_do_vm_incr.__doc__,
                                   help="Reserve VM.")
    parser.add_argument("hostname", type=str, help="location of the vm.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.add_argument("vmname", type=str, help="The VM name.")
    parser.set_defaults(func=_do_vm_reserve)

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_vm_list.__doc__,
                                   help="List vms")
    parser.add_argument("patterns", type=str, default=[], nargs="?",
                        help="list VMs that contain pattern term. "
                        "No pattern means everything.")
    parser.set_defaults(func=_do_vm_list)
    ##

    return subparser
