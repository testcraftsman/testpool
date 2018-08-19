# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
""" Client python API to reserve resources. """

import json
import time
import urllib
import threading
from argparse import Namespace
import requests
import testpool.core.exceptions


class ResourceError(testpool.core.exceptions.TestpoolError):
    """ Thrown when there isn't enough resources. """

    def __init__(self, message):  # pylint: disable=useless-super-delegation
        super(ResourceError, self).__init__(message)


def _renew(*args, **kwargs):
    """ Renew resource acquisition. """
    # pylint: disable=unused-argument

    hndl = args[0]
    hndl.renew()
    interval = hndl.expiration/2
    hndl.threading = threading.Timer(interval, _renew, args=(hndl,))


class ResourceHndl(object):
    """ Acquires a resource and renews its usage until this object is deleted.

    As long as the object exists, the resource acquired will be renewed.
    """
    def __init__(self, ip_addr, pool_name, expiration=60, blocking=False):
        """ Acquire a resource given the parameters.

        @param expiration The time in seconds.
        @param blocking Wait for resource to be available.
        """
        # pylint: disable=invalid-name

        self.pool_name = pool_name
        self.ip_addr = ip_addr
        self.expiration = expiration
        self.blocking = blocking
        self.vm = None
        self.threading = None

    def __enter__(self):
        """ Operations are handled in the constructor. """
        self.acquire(self.blocking)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """ Operations are handled in the constructor. """
        self.release()

    def acquire(self, blocking=None):
        """ Acquire an available resource. """

        self.release()

        blocking = self.blocking if blocking is None else blocking
        params = {"expiration": self.expiration}
        interval = self.expiration/2

        while True:
            try:
                resp = requests.get(self._url_get("acquire"),
                                    urllib.urlencode(params))
                resp.raise_for_status()
                self.vm = json.loads(resp.text,
                                     object_hook=lambda d: Namespace(**d))
                self.threading = threading.Timer(interval, _renew,
                                                 args=(self,))
                self.threading.start()
                return self
            except Exception:
                if blocking:
                    time.sleep(interval)
                    continue
                raise ResourceError("all resources busy or pending")
        return None

    def release(self):
        """ Release resource. """

        if self.threading is None:
            return

        if self.vm is None:
            return

        self.threading.cancel()
        self.threading = None

        requests.get(self._url_get("release"))
        self.vm = None

    def renew(self):
        """ Return usage of the resource. """

        params = {"id": self.vm.id,
                  "expiration": 100}
        requests.get(self._url_get("renew"), urllib.urlencode(params))

    def _url_get(self, action):
        """ Create URL for the given action. """

        ##
        # This should be a config.
        url = "http://%s:8000/testpool/api/v1/" % self.ip_addr
        return url + "pool/%s/%s" % (action, self.pool_name)

    def detail_get(self):
        """ Create URL for the given action. """

        resp = requests.get(self._url_get("detail"))
        resp.raise_for_status()
        return json.loads(resp.text)
