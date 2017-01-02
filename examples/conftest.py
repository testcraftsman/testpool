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
""" Populate test database for examples.

The testpool database must be running in order to see the examples in action.
Examples can run against an installed testpool instance or run the testpool
database manually, like so:

  tpl-db runserver

"""

import logging
import pytest
import testpool.core.database
import testpool.core.commands
import testpool.core.server
import testpool.core.profile

##
# In order to run the examples against a real hypervisor, change this
# IP address. These values are identical to the quick start guide on
# purpose.
GLOBAL = {"hostname": "127.0.0.1",
          "connection": "qemu:///system",
          "profile": "example",
          "count": 3}
##


def teardown_db():
    """ Remove the fake profile used by testing. """

    # logging.info("teardown database")
    # arg_parser = testpool.core.commands.main()
    # cmd = "profile remove %(hypervisor)s %(profile)s --immediate" % GLOBAL
    # args = arg_parser.parse_args(cmd.split())
    # assert testpool.core.commands.args_process(None, args) == 0
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_db(request):
    """ Setup test database for examples. """

    logging.info("setup database")
    ##
    # Check to see if the user has created a test.profile, if not
    # create a fake test.profile. This code would normally not be
    # required. Refer to the quick start guide or installation instruction
    # for setting up a KVM hypervisor

    ##
    # Add a fake.profile to the database.
    arg_parser = testpool.core.commands.main()
    fmt = "profile add %(profile)s kvm %(connection)s test.template %(count)d"
    cmd = fmt % GLOBAL
    args = arg_parser.parse_args(cmd.split())
    assert testpool.core.commands.args_process(None, args) == 0
    ##

    request.addfinalizer(teardown_db)
