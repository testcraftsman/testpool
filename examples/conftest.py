# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
""" Populate test database for examples.

Check to see if the user has created an example test profile, if not
create a fake example profile. A fake example profile uses an in memory
pretent hypervisor. This is sufficient for seeing the Testpool client
API in action and for debugging.

This code would normally not be required. Refer to the quick start guide or
installation instruction for setting up a KVM hypervisor.

"""

import logging
import pytest
import testpool.core.database
import testpool.core.commands
import testpool.core.server
import testpool.core.pool

##
# In order to run the examples against a real hypervisor, change this IP
# address. These values are identical to the quick start guide on purpose.
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
    profiles = testpool.core.profile.profile_list()
    for profile in profiles:
        if profile.host.product != "fake":
            continue
        if profile.name != GLOBAL["profile"]:
            continue
        if profile.host.connection != GLOBAL["connection"]:
            continue
        testpool.core.profile.profile_remove(GLOBAL["profile"], True)


@pytest.fixture(scope="session", autouse=True)
def setup_db(request):
    """ Setup test database for examples. """

    logging.info("setup database")
    ##
    # Check to see if the user has created an example test profile, if not
    # create a fake example profile. This code would normally not be
    # required. Refer to the quick start guide or installation instruction
    # for setting up a KVM hypervisor.
    profiles = testpool.core.profile.profile_list()
    profiles = [item for item in profiles if item.name == GLOBAL["profile"]]
    if len(profiles) == 0:  # pylint: disable=len-as-condition
        testpool.core.profile.profile_add(GLOBAL["connection"], "fake",
                                          GLOBAL["profile"], GLOBAL["count"],
                                          "test.template")

    request.addfinalizer(teardown_db)
