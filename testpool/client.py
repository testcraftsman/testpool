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
""" Client python API to reserve VMs. """

import json
import time
import requests
import urllib
import threading
from argparse import Namespace


def _renew(*args, **kwargs):
    """ Renew VM acquisition. """
    hndl = args[0]
    hndl.renew()
    interval = hndl.expiration/2
    hndl.threading = threading.Timer(interval, _renew, args=(hndl,))


class VMHndl(object):
    """ Acquires a VM and renews its usage until this object is deleted.

    As long as the object exists, the VM acquired will be renewed.
    """

    def __init__(self, ip_addr, profile_name, expiration=10):
        """ Acquire a VM given the parameters.

        @param expiration The time in seconds.
        """
        self.profile_name = profile_name
        self.ip_addr = ip_addr
        self.expiration = expiration

        params = {"expiration": expiration}

        resp = requests.get(self._url_get("acquire"), urllib.urlencode(params))
        resp.raise_for_status()
        self.vm = json.loads(resp.text, object_hook=lambda d: Namespace(**d))

        interval = self.expiration/2
        self.threading = threading.Timer(interval, _renew, args=(self,))
        self.threading.start()

    def __enter__(self):
        """ Operations are handled in the constructor. """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """ Operations are handled in the constructor. """
        self.release()

    def release(self):
        """ Release VM resource. """

        self.threading.cancel()
        requests.get(self._url_get("release"))

    def renew(self):
        """ Return usage of the VM. """

        params = {"id": self.vm.id,
                  "expiration": 100}
        resp = requests.get(self._url_get("renew"), urllib.urlencode(params))

    def _url_get(self, action):
        """ Create URL for the given action. """

        ##
        # This should be a config.
        url = "http://%s:8000/testpool/api/" % self.ip_addr
        return url + "profile/%s/%s" % (action, self.profile_name)
