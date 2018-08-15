# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
"""
Contains functionality common to extensions.
Handles logging.
"""
import logging
import testpool.settings


def create():
    """ Create logger for tbd application. """

    logger = logging.getLogger("testpool")
    logger.propagate = False

    if len(logger.handlers) == 0:
        formatter = logging.Formatter(testpool.settings.FMT,
                                      "%Y-%m-%d %H:%M:%S")
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger


def args_process(logger, args):
    """ Process any generic parameters. """

    if args.verbose == 1:
        logger.setLevel(level=logging.INFO)
        logger.info("verbosity level set to INFO")
    elif args.verbose > 1:
        logger.setLevel(level=logging.DEBUG)
        logger.info("verbosity level set to DEBUG")

    return logger
