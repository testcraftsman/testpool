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
import testpool.core.algo
from testpooldb import models

LOGGER = logging.getLogger("testpool.core.profile")


def profile_remove(hostname, profile, immediate):
    """ Remove a profile.

    Profiles can't be removed immediately, VMs are marked for purge
    and when all VMs are gone the profile will be removed.
    """
    LOGGER.debug("profile_remove %s %s", hostname, profile)
    try:
        profile = models.Profile.objects.get(name=profile,
                                             hv__hostname=hostname)
        LOGGER.debug("found profile %s %s", hostname, profile)
        profile.vm_max = 0
        profile.save()

        delta = 0
        for vmh in profile.vm_set.all():
            if immediate:
                vmh.delete()
            else:
                vmh.transition(models.VM.RESERVED,
                               testpool.core.algo.ACTION_DESTROY, delta)
                delta += 60

        if immediate:
            profile.delete()
        return 0
    except models.Profile.DoesNotExist:
        LOGGER.debug("profile %s on %s not found", profile, hostname)
        return 1


def find(hostname, product, profile):
    """ Find and profiles that match the content provided. """

    results = models.Profile.objects.all()
    if profile:
        results = results.filter(name=profile)
    if hostname:
        results = results.filter(hv__hostname=hostname)
    if product:
        results = results.filter(hv__product=product)

    return results


def profile_add(hostname, product, profile, vm_max, template):
    """ Add a profile. """

    (hv1, _) = models.HV.objects.get_or_create(hostname=hostname,
                                               product=product)
    defaults = {"vm_max": vm_max, "template_name": template}
    (profile1, _) = models.Profile.objects.update_or_create(name=profile,
                                                            hv=hv1,
                                                            defaults=defaults)

    ##
    # Check to see if the number of VMs should change.
    exts = testpool.core.ext.api_ext_list()
    vmpool = exts[product].vmpool_get(profile1)
    testpool.core.algo.adapt(vmpool, profile1)
    ##

    return 0


def _do_profile_remove(args):
    """ Remove a profile. """

    return profile_remove(args.hostname, args.profile, args.immediate)


def _do_profile_add(args):
    """ Add or modify a profile.

    If the profile exists, calling this again will change the maximum number
    of VMS and the template name. The connection parameter supported format:
    account@hypervisor account and hostname of the hypervisor.

    """

    LOGGER.info("add a profile %s", args.profile)

    extensions = testpool.core.ext.list_get()

    if args.product not in extensions:
        LOGGER.debug("acceptable extensions are:")
        for extension in extensions:
            LOGGER.debug("  " + extension)

        raise ValueError("product %s not supported" % args.product)

    return profile_add(args.connection, args.product, args.profile, args.max,
                       args.template)


def _do_profile_list(_):
    """ List all profiles. """
    fmt = "%-16s %-16s %-8s %-20s %-5s"

    LOGGER.info("list profiles")

    print fmt % ("Hostname", "Name", "Product", "Template", "VMs")
    for profile in models.Profile.objects.all():
        current = profile.vm_set.filter(status=models.VM.READY).count()
        print fmt % (profile.hv.hostname, profile.name, profile.hv.product,
                     profile.template_name,
                     "%s/%s" % (current, profile.vm_max))
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
    parser.add_argument("connection", type=str,
                        help="How to connect to the hypervisor. Format "
                        "depends on how to connect to the hypervisor")
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
    parser.add_argument("--immediate", action="store_true",
                        help="Remove profile content from the database."
                        "Do not wait for VMs to be purged")
    ##

    return subparser
