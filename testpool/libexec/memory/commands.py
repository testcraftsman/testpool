# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testbed
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
CLI for testsuites.
"""
import logging
from . import api

CONTEXT = "default"


def do_add_testsuite(args):
    """ Add a testsuite to the database. """

    logging.info("adding testsuite %s", args.name)
    api.add_testsuite(args.testplan, args.context, args.name, args.build, [])


def do_list_testsuite(args):
    """ List testsuites based on search criteria. """

    from testdb import models
    logging.info("listing testsuites")
    context = models.Context.objects.get(name=args.context)
    testsuites = models.Testsuite.filter(context, args.filter, keys=[])
    for testsuite in testsuites:
        print testsuite


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("testsuite", help=__doc__)
    parser.add_argument("--testplan", default=None,
                        help="identifies specific testplan.")
    parser.add_argument("--context", default=CONTEXT, type=str,
                        help="Testsuite context.")
    subparser = parser.add_subparsers()

    ##
    # Add
    parser = subparser.add_parser("add",
                                  description="Add a testsuite",
                                  help="Add a testsuite.")
    parser.set_defaults(func=do_add_testsuite)
    parser.add_argument("name", type=str, help="Name of the testsuite.")
    parser.add_argument("build", type=str,
                        help="Build associated with the testsuite.")

    ##
    # List
    parser = subparser.add_parser("list",
                                  description="List all of the testsuites.",
                                  help="List testsuite.")
    parser.add_argument("--filter", type=str, help="Filter testsuites")
    parser.set_defaults(func=do_list_testsuite)

    ##
    # CLI for adding testsuite keys
    # Keys are how testsuites are organized and searched in the database.
    parser = subparser.add_parser("key",
                                  help="APIs for manipulating testsuite keys")
    subparser = parser.add_subparsers()
    parser = subparser.add_parser("add",
                                  description="Add a testsuite key",
                                  help="Add a testsuite key.")

    ##
    # List
    return subparser
