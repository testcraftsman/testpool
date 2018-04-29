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
import testpool.core.ext
import testpool.core.algo
from testpooldb import models

LOGGER = logging.getLogger("testpool.core.profile")


def profile_remove(profile, immediate):
    """ Remove a profile.

    Profiles can't be removed immediately, Resources are marked for purge
    and when all Resources are gone the profile will be removed.
    """
    LOGGER.debug("profile_remove %s", profile)
    try:
        profile = models.Profile.objects.get(name=profile)
        LOGGER.debug("found profile %s", profile)
        profile.resource_max = 0
        profile.save()

        delta = 0
        for rsrc in profile.resource_set.all():
            if immediate:
                rsrc.delete()
            else:
                rsrc.transition(models.Resource.RESERVED,
                                testpool.core.algo.ACTION_DESTROY, delta)
                delta += 60

        if immediate:
            profile.delete()
        return 0
    except models.Profile.DoesNotExist:
        LOGGER.warning("profile %s not found", profile)
        return 1


def profile_add(connection, product, profile, resource_max, template):
    """ Add a profile. """

    (hv1, _) = models.HV.objects.get_or_create(connection=connection,
                                               product=product)
    defaults = {"resource_max": resource_max, "template_name": template}
    (profile1, _) = models.Profile.objects.update_or_create(name=profile,
                                                            hv=hv1,
                                                            defaults=defaults)

    ##
    # Check to see if the number of Resources should change.
    exts = testpool.core.ext.api_ext_list()
    pool = exts[product].pool_get(profile1)
    testpool.core.algo.adapt(pool, profile1)
    ##

    return 0


def _do_profile_remove(args):
    """ Remove a profile. """

    return profile_remove(args.profile, args.immediate)


def _do_profile_add(args):
    """ Add or modify a profile.

    If the profile exists, calling this again will change the maximum number
    of ResourceS and the template name. The connection parameter supported
    format: account@hypervisor account and connection of the hypervisor.
    """

    LOGGER.info("add a profile %s", args.profile)

    extensions = testpool.core.ext.list_get()

    if args.product not in extensions:
        LOGGER.debug("acceptable extensions are:")
        for extension in extensions:
            LOGGER.debug("  %s", extension)

        raise ValueError("product %s not supported" % args.product)

    return profile_add(args.connection, args.product, args.profile, args.max,
                       args.template)


def _do_profile_detail(args):
    """ show details of a profile. """

    for profile in models.Profile.objects.all():
        contains = [srch in profile for srch in args.srch]

        if all(contains):
            print "name:     ", profile.name
            print "template: ", profile.template_name
            print "status:   ", profile.status_str()
            print "Resources available: ", profile.resource_available()
            print "Resources maximum:   ", profile.resource_max

            ##
            # Check to see if the number of Resources should change.
            exts = testpool.core.ext.api_ext_list()
            pool = exts[profile.hv.product].pool_get(profile)
            info = pool.info_get()

            print "Model:          " + str(info.model)
            print "Memory size:    " + str(info.memory_size) + 'MB'
            print "Number of CPUs: " + str(info.cpus)
            print "MHz of CPUs:    " + str(info.cpu_mhz)
            print "NUMA nodes:  " + str(info.numa_nodes)
            print "CPU sockets: " + str(info.cpu_sockets)
            print "CPU cores per socket: " + str(info.cores_per_socket)
            print "CPU threads per core: " + str(info.threads_per_core)
            ##


def profile_list():
    """ Return a list of profiles. """

    for profile in models.Profile.objects.all():
        current = profile.resource_set.filter(
            status=models.Resource.READY).count()
        profile.current = current
        yield profile


def _do_profile_list(_):
    """ List all profiles. """
    fmt = "%-12s %-5s %-32s %-16s %-5s %-5s"

    LOGGER.info("list profiles")

    # \todo provide a dynamically adjusting column width
    print fmt % ("Name", "Prod", "Connection", "Template", "Resources",
                 "Status")
    for profile in profile_list():
        print fmt % (profile.name, profile.hv.product, profile.hv.connection,
                     profile.template_name,
                     "%s/%s" % (profile.current, profile.resource_max),
                     profile.status_str())
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
    parser.add_argument("profile", type=str, help="Name of the fake profile.")
    parser.add_argument("product", type=str, help="The type of product.")
    parser.add_argument("connection", type=str,
                        help="How to connect to the hypervisor. Format "
                        "depends on how to connect to the hypervisor")
    parser.add_argument("template", type=str,
                        help="Number of Resource to manage.")
    parser.add_argument("max", type=int, help="Number of Resource to manage.")
    ##

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_profile_list.__doc__,
                                   help="List profiles")
    parser.set_defaults(func=_do_profile_list)
    ##

    ##
    # Details
    parser = rootparser.add_parser("detail",
                                   description=_do_profile_detail.__doc__,
                                   help="Show profile details.")
    parser.add_argument("srch", type=str, nargs="*",
                        help="Show profiles that match the srch.")
    parser.set_defaults(func=_do_profile_detail)
    ##

    ##
    # Remove
    parser = rootparser.add_parser("remove",
                                   description=_do_profile_remove.__doc__,
                                   help="Remove a profile")
    parser.set_defaults(func=_do_profile_remove)
    parser.add_argument("profile", type=str, help="Profile name to delete.")
    parser.add_argument("--immediate", action="store_true",
                        help="Remove profile content from the database."
                        "Do not wait for Resources to be purged")
    ##

    return subparser
