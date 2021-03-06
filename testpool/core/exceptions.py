"""
Provide infrastructure for defining and supporting exceptions.
"""
import sys
import logging

from testpool.core import logger

LOG = logger.create()


class TestpoolError(Exception):
    """ Common to all Testpool exceptions. """

    def __init__(self, message):  # pylint: disable=W0235
        """ Constructor. """
        super(TestpoolError, self).__init__(message)


class ConnectionError(Exception):
    """ When unable to connect to a resource. """

    def __init__(self, message):  # pylint: disable=W0235
        """ Constructor. """
        super(ConnectionError, self).__init__(message)


class PoolError(TestpoolError):
    """ Thrown when a pool is considered bad. """

    def __init__(self, message, pool_error):
        """ Constructor. """
        super(PoolError, self).__init__(message)
        self.pool = pool_error


# pylint: disable=W0703
def try_catch(func):
    """ Call func with args and catch all errors. """
    try:
        return func()
    except PoolError, arg:
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.exception(arg)
        else:
            LOG.error(arg)

        stack_trace = sys.exc_info()[2]
        arg.pool.stacktrace_set(str(arg), stack_trace)
        return 1
