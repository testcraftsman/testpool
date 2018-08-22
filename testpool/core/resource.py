# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
"""
Fake pools used for development.

This pool pretends to manage a pool of Resources which are merely pretend
ResourceS which do not exist.
"""
import logging
from django.db.models import Q
from testpool.core import algo
from testpool.core import ext
from testpooldb import models


def _pool_get(connection, product, pool):
    """ Return the pool given the parameters. """

    host1 = models.Host.objects.get(connection=connection, product=product)
    return models.Pool.objects.get(name=pool, host=host1)


def _do_resource_incr(args):
    """ Increment or decrement the number of Resources. """

    logging.info("%s: incrementing mx Resources %d", args.pool, args.count)
    pool1 = models.Pool.objects.get(name=args.pool)
    pool1.resource_max += args.count
    pool1.save()

    return 0


def _do_resource_release(args):
    """ Release Resource. """

    logging.info("release %s %s", args.pool, args.name)
    rsrc = models.Resource.objects.get(name=args.name,
                                       pool__name=args.pool)
    rsrc.transition(models.Resource.PENDING, algo.ACTION_DESTROY, 0)
    rsrc.save()
    return 0


def _do_resource_reserve(args):
    """ Reserve Resource. """

    logging.info("reserve %s %s", args.pool, args.name)
    rsrc = models.Resource.objects.get(name=args.name,
                                       pool__name=args.pool)
    rsrc.status = models.Resource.RESERVED
    rsrc.save()
    return 0


def _do_resource_detail(args):
    """ Resource Detail content. """

    rsrc = models.Resource.objects.get(pool__name=args.pool,
                                       name=args.name)

    exts = ext.api_ext_list()
    pool = exts[rsrc.pool.host.product].pool_get(rsrc.pool)

    print "Name: %s" % args.name
    ip_address = pool.ip_get(args.name)
    print "IP: %s" % ip_address


def _do_resource_list(args):
    """ List all resources which contains patterns. """

    fmt = "%-25s %-8s %-16s %s"

    logging.info("%s: list resources", args.pool)
    rsrcs = models.Resource.objects.filter(pool__name=args.pool)

    print fmt % ("Name", "Status", "IP", "Reserved Time")
    for rsrc in rsrcs:
        print fmt % (rsrc.name, models.Resource.status_to_str(rsrc.status),
                     rsrc.ip_addr, rsrc.action_time)


def _do_resource_contain(args):
    """ List all resources which contains patterns. """

    fmt = "%-7s %-16s %-13s %-8s %-16s %s"

    logging.info("list resources by %s", args.patterns)
    rsrcs = models.Resource.objects.all()
    for pattern in args.patterns:
        rsrcs = rsrcs.filter(
            Q(name__contains=pattern) |
            Q(pool__host__connection__contains=pattern) |
            Q(pool__host__product__contains=pattern) |
            Q(pool__name__contains=pattern)).order_by("name")

    print fmt % ("Pool", "Connection", "Name", "Status", "IP",
                 "Reserved Time")
    for rsrc in rsrcs:
        print fmt % (rsrc.pool.name, rsrc.pool.host.connection,
                     rsrc.name, models.Resource.status_to_str(rsrc.status),
                     rsrc.ip_addr, rsrc.action_time)

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
    parser.add_argument("pool", type=str, help="The pool name to clone.")
    parser.add_argument("--count", type=int, default=1,
                        help="Increment/decrement the maximum number "
                        "of resources.")
    ##

    parser = rootparser.add_parser("release",
                                   description=_do_resource_incr.__doc__,
                                   help="Release Resource to be reclaimed.")
    parser.add_argument("pool", type=str, help="The pool name to clone.")
    parser.add_argument("name", type=str, help="The Resource name.")
    parser.set_defaults(func=_do_resource_release)

    parser = rootparser.add_parser("reserve",
                                   description=_do_resource_incr.__doc__,
                                   help="Reserve Resource.")
    parser.add_argument("pool", type=str, help="Pool name.")
    parser.add_argument("name", type=str, help="The Resource name.")
    parser.set_defaults(func=_do_resource_reserve)

    ##
    # List
    parser = rootparser.add_parser("list",
                                   description=_do_resource_list.__doc__,
                                   help="List resources that contain pattern")
    parser.add_argument("pool", type=str,
                        help="list Resources that for pool")
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
    parser.add_argument("pool", type=str, help="Pool name")
    parser.add_argument("name", type=str, help="Resource name")
    parser.set_defaults(func=_do_resource_detail)
    ##

    return subparser
