#!/usr/bin/python
"""
  Validate the tpl configuration.
"""
import os
import sys
import logging
import argparse

logging.getLogger().setLevel(level=logging.WARNING)
logging.getLogger("django.db.backends").setLevel(logging.CRITICAL)


def do_check(args):
    """ Check --log content. """

    from testpool.core import cfgcheck

    if not cfgcheck.check(args.log):
        raise ValueError("%s does not exist" % args.log)


def argparser():
    """Create server arg parser. """

    parser = argparse.ArgumentParser(prog="tplcfgcheck")
    parser.add_argument('log',
                        help="Validate configuration conten.")
    parser.add_argument('--verbose', '-v', required=False, action="count",
                        help="enable debug verbosity.")
    parser.set_defaults(func=do_check)

    return parser


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


def main():
    """ main entry point. """

    parser = argparser()
    args = parser.parse_args()

    logger = logging.getLogger()
    if args.verbose == 1:
        logger.setLevel(level=logging.INFO)
        logger.info("verbosity level set to INFO")
    elif args.verbose > 1:
        logger.setLevel(level=logging.DEBUG)
        logger.info("verbosity level set to DEBUG")

    args.func(args)


# pylint: disable=W0703
if __name__ == "__main__":
    try:
        env_setup()
        main()
    except Exception, arg:
        logging.exception(arg)
        sys.exit(1)
