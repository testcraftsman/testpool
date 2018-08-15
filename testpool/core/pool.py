# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
"""
Fake pools used for development.

This pool pretends to manage a pool of Resources which are merely pretend
ResourceS which do not exist.
"""
import logging
import testpool.core.ext
import testpool.core.algo
from testpooldb import models

LOGGER = logging.getLogger(__name__)


def _do_pool_remove(args):
    """ Remove a pool.

    Pools can't be removed immediately, Resources are marked for purge
    and when all Resources are gone the pool will be removed.
    """

    LOGGER.debug("pool_remove %s", args.pool)
    try:
        testpool.core.algo.pool_remove(args.pool, args.immediate)
        return 0
    except models.Pool.DoesNotExist:
        LOGGER.warning("pool %s not found", args.pool)
        return 1


def _do_pool_add(args):
    """ Add or modify a pool.

    If the pool exists, calling this again will change the maximum number
    of ResourceS and the template name. The connection parameter supported
    format: account@hypervisor account and connection of the hypervisor.
    """

    LOGGER.info("add a pool %s", args.pool)

    extensions = testpool.core.ext.list_get()

    if args.product not in extensions:
        LOGGER.debug("acceptable extensions are:")
        for extension in extensions:
            LOGGER.debug("  %s", extension)

        raise ValueError("product %s not supported" % args.product)

    testpool.core.algo.pool_add(args.connection, args.product, args.pool,
                                args.max, args.template)
    return 0


def _do_pool_detail(args):
    """ show details of a pool. """

    for pool in models.Pool.objects.all():
        contains = [srch in pool for srch in args.srch]

        if all(contains):
            print "name:     ", pool.name
            print "template: ", pool.template_name
            print "status:   ", pool.status_str()
            print "Resources available: ", pool.resource_available()
            print "Resources maximum:   ", pool.resource_max

            ##
            # Check to see if the number of Resources should change.
            exts = testpool.core.ext.api_ext_list()
            pool = exts[pool.host.product].pool_get(pool)
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


def _do_pool_list(_):
    """ List all pools. """
    fmt = "%-12s %-5s %-32s %-16s %-5s %-5s"

    LOGGER.info("list pools")

    # \todo provide a dynamically adjusting column width
    print fmt % ("Name", "Prod", "Connection", "Template", "Resources",
                 "Status")
    for pool in models.Pool.objects.all():
        current = pool.resource_available()
        print fmt % (pool.name, pool.host.product,
                     pool.host.connection, pool.template_name,
                     "%s/%s" % (current, pool.resource_max),
                     pool.status_str())
    return 0


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("pool",
                                  help="Commands to manage fake pools",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Add
    parser = rootparser.add_parser("add", description=_do_pool_add.__doc__,
                                   help="Add a pool")
    parser.set_defaults(func=_do_pool_add)
    parser.add_argument("pool", type=str, help="Name of the fake pool.")
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
                                   description=_do_pool_list.__doc__,
                                   help="List pools")
    parser.set_defaults(func=_do_pool_list)
    ##

    ##
    # Details
    parser = rootparser.add_parser("detail",
                                   description=_do_pool_detail.__doc__,
                                   help="Show pool details.")
    parser.add_argument("srch", type=str, nargs="*",
                        help="Show pools that match the srch.")
    parser.set_defaults(func=_do_pool_detail)
    ##

    ##
    # Remove
    parser = rootparser.add_parser("remove",
                                   description=_do_pool_remove.__doc__,
                                   help="Remove a pool")
    parser.set_defaults(func=_do_pool_remove)
    parser.add_argument("pool", type=str, help="Pool name to delete.")
    parser.add_argument("--immediate", action="store_true",
                        help="Remove pool content from the database."
                        "Do not wait for Resources to be purged")
    ##

    return subparser
