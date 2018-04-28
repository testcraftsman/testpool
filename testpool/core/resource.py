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

This profile pretends to manage a pool of Resources which are merely pretend
ResourceS which do not exist.
"""
import logging
from django.db.models import Q
from testpool.core import algo
from testpool.core import ext
from testpooldb import models


def _profile_get(connection, product, profile):
    """ Return the profile given the parameters. """

    hv1 = models.HV.objects.get(connection=connection, product=product)
    return models.Profile.objects.get(name=profile, hv=hv1)


def _do_resource_incr(args):
    """ Increment or decrement the number of Resources. """

    logging.info("%s: incrementing mx Resources %d", args.profile, args.count)
    profile1 = models.Profile.objects.get(name=args.profile)
    profile1.vm_max += args.count
    profile1.save()

    return 0


def _do_resource_release(args):
    """ Release Resource. """

    logging.info("release %s %s", args.profile, args.name)
    vm1 = models.Resource.objects.get(name=args.name,
                                      profile__name=args.profile)
    vm1.transition(models.Resource.PENDING, algo.ACTION_DESTROY, 0)
    vm1.save()
    return 0


def _do_resource_reserve(args):
    """ Reserve Resource. """

    logging.info("reserve %s %s", args.profile, args.name)
    vm1 = models.Resource.objects.get(name=args.name,
                                      profile__name=args.profile)
    vm1.status = models.Resource.RESERVED
    vm1.save()
    return 0


def _do_resource_detail(args):
    """ Resource Detail content. """

    vm1 = models.Resource.objects.get(profile__name=args.profile,
                                      name=args.name)

    exts = ext.api_ext_list()
    vmpool = exts[vm1.profile.hv.product].pool_get(vm1.profile)

    print "Name: %s" % args.name
    ip_address = vmpool.ip_get(args.name)
    print "IP: %s" % ip_address


def _do_resource_list(args):
    """ List all resources which contains patterns. """

    fmt = "%-25s %-8s %-16s %s"

    logging.info("%s: list resources", args.profile)
    vms = models.Resource.objects.filter(profile__name=args.profile)

    print fmt % ("Name", "Status", "IP", "Reserved Time")
    for vm1 in vms:
        print fmt % (vm1.name, models.Resource.status_to_str(vm1.status),
                     vm1.ip_addr, vm1.action_time)


def _do_resource_contain(args):
    """ List all resources which contains patterns. """

    fmt = "%-7s %-16s %-13s %-8s %-16s %s"

    logging.info("list resources by %s", args.patterns)
    vms = models.Resource.objects.all()
    for pattern in args.patterns:
        vms = vms.filter(
            Q(name__contains=pattern) |
            Q(profile__hv__connection__contains=pattern) |
            Q(profile__hv__product__contains=pattern) |
            Q(profile__name__contains=pattern)).order_by("name")

    print fmt % ("Profile", "Connection", "Name", "Status", "IP",
                 "Reserved Time")
    for vm1 in vms:
        print fmt % (vm1.profile.name, vm1.profile.hv.connection, vm1.name,
                     models.Resource.status_to_str(vm1.status), vm1.ip_addr,
                     vm1.action_time)

    return 0


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("resource",
                                  help="Commands to manage fake resources",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Increment
    parser = rootparser.add_parser("incr",
                                   description=_do_resource_incr.__doc__,
                                   help="Increment the number of Resources")
    parser.set_defaults(func=_do_resource_incr)
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.add_argument("--count", type=int, default=1,
                        help="Increment/decrement the maximum number "
                        "of resources.")
    ##

    parser = rootparser.add_parser("release",
                                   description=_do_resource_incr.__doc__,
                                   help="Release Resource to be reclaimed.")
    parser.add_argument("profile", type=str, help="The profile name to clone.")
    parser.add_argument("name", type=str, help="The Resource name.")
    parser.set_defaults(func=_do_resource_release)

    parser = rootparser.add_parser("reserve",
                                   description=_do_resource_incr.__doc__,
                                   help="Reserve Resource.")
    parser.add_argument("profile", type=str, help="Profile name.")
    parser.add_argument("name", type=str, help="The Resource name.")
    parser.set_defaults(func=_do_resource_reserve)

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_resource_list.__doc__,
                                   help="List resources that contain pattern")
    parser.add_argument("profile", type=str,
                        help="list Resources that for profile")
    parser.set_defaults(func=_do_resource_list)
    ##

    ##
    # Contains
    parser = rootparser.add_parser("contains",
                                   description=_do_resource_contain.__doc__,
                                   help="List resources that contain pattern")
    parser.add_argument("patterns", type=str, default=[], nargs="?",
                        help="list Resources that contain pattern term. "
                        "No pattern means everything.")
    parser.set_defaults(func=_do_resource_contain)
    ##

    ##
    # List
    parser = rootparser.add_parser("detail",
                                   description=_do_resource_detail.__doc__,
                                   help="Show Resource details")
    parser.add_argument("profile", type=str, help="Profile name")
    parser.add_argument("name", type=str, help="Resource name")
    parser.set_defaults(func=_do_resource_detail)
    ##

    return subparser
