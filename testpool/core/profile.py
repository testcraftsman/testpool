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
import testpool.core.ext
from testpooldb import models


def profile_remove(hostname, profile):
    """ Remove a profile. """

    try:
        profile = models.Profile.objects.get(name=profile,
                                             hv__hostname=hostname)
        profile.delete()
    except models.Profile.DoesNotExist:
        pass

    try:
        hv1 = models.HV.objects.get(hostname=hostname)
        if hv1.profile_set.count() == 0:
            #profiles = models.Profile.objects.filter(hv=hv1)
            #if profiles.count() == 0:
            hv1.delete()
    except models.HV.DoesNotExist:
        return 0


def profile_add(hostname, product, profile, vm_max, template):
    """ Add a profile. """

    (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                               product=product)
    defaults = {"vm_max": vm_max, "template_name": template}
    models.Profile.objects.update_or_create(name=profile, hv=hv1,
                                            defaults=defaults)
    return 0


def _do_profile_remove(args):
    """ Remove a profile. """

    logging.info("remove a profile %s", args.profile)
    profile_remove(args.hostname, args.profile)
    return 0


def _do_profile_add(args):
    """ Add or modify a profile.

    If the profile exists, calling this again will change the maximum number
    of VMS and the template name.
    """

    logging.info("add a profile %s", args.profile)

    extensions = testpool.core.ext.list_get()

    if args.product not in extensions:
        logging.debug("acceptable extensions are:")
        for extension in extensions:
            logging.debug("  " + extension)
        raise ValueError("product %s not supported" % args.profile)

    return profile_add(args.hostname, args.product, args.profile, args.max,
                       args.template)


def _do_profile_list(_):
    """ List all profiles. """
    fmt = "%-16s %-8s %-20s %-3s %s"

    logging.info("list profiles")

    print fmt % ("Hostname", "Product", "Name", "VMs", "Template")
    for profile in models.Profile.objects.all():
        current = profile.vm_set.count()
        print fmt % (profile.hv.hostname, profile.hv.product, profile.name,
                     "%s/%s" % (current, profile.vm_max),
                     profile.template_name)

    return 0


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("profile",
                                  help="Commands to manage fake profiles",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Add
    parser = rootparser.add_parser("add", description=_do_profile_add.__doc__,
                                   help="Add a profile")
    parser.set_defaults(func=_do_profile_add)
    parser.add_argument("hostname", type=str, help="location of the profile.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("profile", type=str, help="Name of the fake profile.")
    parser.add_argument("template", type=str, help="Number of VM to manage.")
    parser.add_argument("max", type=int, help="Number of VM to manage.")
    ##

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_profile_list.__doc__,
                                   help="List profiles")
    parser.set_defaults(func=_do_profile_list)
    ##

    ##
    # Remove
    parser = rootparser.add_parser("remove",
                                   description=_do_profile_remove.__doc__,
                                   help="Remove a profile")
    parser.set_defaults(func=_do_profile_remove)
    parser.add_argument("hostname", type=str, help="location of the profile.")
    parser.add_argument("profile", type=str, help="Name of the fake profile.")
    ##

    return subparser
