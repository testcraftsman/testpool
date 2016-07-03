"""
Handles logging.
"""
import logging
import testpool.settings


def create():
    """ Create logger for tbd application. """
    console = logging.StreamHandler()
    formatter = logging.Formatter(testpool.settings.FMT)
    console.setFormatter(formatter)
    logger = logging.getLogger("")
    logger.addHandler(console)
    logger.setLevel(logging.WARNING)

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
