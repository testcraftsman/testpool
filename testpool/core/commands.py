# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
"""
Contains functionality common to extensions.
"""
import sys
import logging
import importlib
import pkgutil
import argparse
import traceback
import unittest
import testpool.settings
import testpool.version
from testpool.core import logger
from testpool.core import pool
from testpool.core import resource


def args_process(log_hndl, args):
    """ Process any generic parameters. """

    if log_hndl:
        logger.args_process(log_hndl, args)
    return args.func(args)


def argparser(progname):
    """ Create top level argument parser. """

    arg_parser = argparse.ArgumentParser(prog=progname)
    arg_parser.add_argument('--version', action="version",
                            version=testpool.version.PACKAGE_VERSION)
    arg_parser.add_argument('--verbose', '-v', required=False, action="count",
                            help="enable debug verbosity.")
    return arg_parser


def onerror(name):
    """ Show module that fails to load. """
    logging.error("importing module %s", name)

    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)


def extensions_find(arg_parser):
    """ Look for command extensions. """

    subparser = arg_parser.add_subparsers(
        title="subcommands", description="Valid subcommands",
        help="Each subcommands supports --help for additional information.")

    ##
    # Add common commands.
    pool.add_subparser(subparser)
    resource.add_subparser(subparser)
    ##

    for package in testpool.settings.PLUGINS:
        logging.debug("loading commands %s", package)

        package = importlib.import_module(package)
        for _, module, ispkg in pkgutil.walk_packages(package.__path__,
                                                      package.__name__ + ".",
                                                      onerror=onerror):
            ##
            # only include commands from commands.py files.
            if ispkg or not module.endswith("commands"):
                continue
            logging.debug("  loading commands from %s", module)
            module = importlib.import_module(module)
            try:
                module.add_subparser(subparser)
            except AttributeError, arg:
                ##
                # This means that the module is missing the add method.
                # All modules identified in settings to extend CLI
                # must have an add method
                logging.error("adding subparser for %s.%s", package, module)
                logging.exception(arg)


def main():
    """ Entry point for parsing tbd arguments. """
    arg_parser = argparser("tpl")
    extensions_find(arg_parser)
    return arg_parser


class Testsuite(unittest.TestCase):
    """ Test commands. """

    def test_bad_pool(self):
        """ Test that bad pools are prevented. """

        arg_parser = main()
        cmd = "pool add localhost bad bad.pool bad.template 10"
        args = arg_parser.parse_args(cmd.split())
        with self.assertRaises(ValueError):
            args_process(None, args)

    def test_resource_incr(self):
        """ Test that bad pools are prevented. """

        arg_parser = main()

        cmd = "pool add test.pool fake localhost test.template 10"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(args_process(None, args), 0)

        cmd = "resource incr test.pool"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(args_process(None, args), 0)

        cmd = "resource incr test.pool --count 2"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(args_process(None, args), 0)

        cmd = "pool remove test.pool"
        args = arg_parser.parse_args(cmd.split())
        self.assertEqual(args_process(None, args), 0)
