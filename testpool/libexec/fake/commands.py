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
import profile

CONTEXT = "default"


def do_fake_add(args):
    """ Add or modify an fake profile.
    If the fake profile exists, calling this again will change the
    maximum number of VMS and the template name.
    """

    logging.info("fake adding profile%s", args.profile)
    profile.add("localhost", "fake", args.profile, args.max,
                args.template_name)


def add_subparser(subparser):
    """ Create testsuite CLI commands. """

    parser = subparser.add_parser("fake",
                                  help="Commands to manage fake profiles",
                                  description=__doc__)
    rootparser = parser.add_subparsers()

    ##
    # Add
    parser = rootparser.add_parser("profile",
                                   description="profile commands",
                                   help="Add a testsuite.")
    rootparser = parser.add_subparsers()
    parser = rootparser.add_parser("add",
                                   description="Add a profile",
                                   help="Add a testsuite.")
    parser.set_defaults(func=do_fake_add)
    parser.add_argument("profile", type=str, help="Name of the fake profile.")
    parser.add_argument("template-name", type=str,
                        help="Number of VM to manage.")
    parser.add_argument("max", type=int, help="Number of VM to manage.")
    ##

    return subparser
