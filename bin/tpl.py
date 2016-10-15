#!/usr/bin/python
"""
Single entry point for test bed CLI.
"""
import os
import sys
import logging


def parse():
    """ main entry point. """
    from testpool.core import commands
    from testpool.core import logger

    logger = logger.create()

    arg_parser = commands.main()
    args = arg_parser.parse_args()
    return commands.args_process(logger, args)


def env_setup():
    """ Main entry point.

    If calling tbd from within a .git clone append the appropriate
    testpool directory clone otherwise python content is stored
    under the normal site-packages.
    """

    ##
    # If the git directory exists, at this location then this script
    # is part of a git clone.
    git_dir = os.path.abspath(os.path.join(__file__, "..", "..", ".git"))
    if os.path.exists(git_dir):
        ##
        # This path is necessary to load anything under testpool clone.
        testpool_dir = os.path.abspath(os.path.join(__file__, "..", ".."))
        sys.path.insert(0, testpool_dir)


# pylint: disable=W0703
if __name__ == "__main__":
    try:
        env_setup()
        # pylint: disable=C0413
        from testpool.core import database

        database.init()
        sys.exit(parse())
    except Exception, arg:
        logging.exception(arg)
        sys.exit(1)
