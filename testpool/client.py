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
import threading
import argparse import Namespace


def renew(obj):
    """ Renew VM acquisition. """
    obj.renew()


class VMHndl(object):
    """ Acquires a VM and renews its usage until this object is deleted.

    As long as the object exists, the VM acquired will be renewed.
    """

    def __init__(self, hostname, profile_name, expiration=120):
        """ Acquire a VM given the parameters.
        @param expiration The time in seconds.
        """

        self.profile_name = profile_name
        self.hostname = hostname

        params = {"expiration": 100}

        resp = requests.get(url_get("acquire"), urllib.urlencode(params))
        resp.raise_for_status()
        self.vm = json.loads(resp.text,
                             object_hook=lambda d: Namespace(**d)))

        interval = expiration/2
        thgreading.Timer(interval, _renew, self).start()

    def renew(self):
        """ Return usage of the VM. """

        params = {"id": self.vm.id,
                  "expiration": 100}
        resp = requests.get(url_get("renew"), urllib.urlencode(params))

        interval = expiration/2
        thgreading.Timer(interval, _renew, self).start()

    def _url_get(self, action):
        """ Create URL for the given action. """

        url = "http://%s:8000/testpool/api/" % self.hostname
        return self.url + "profile/%s/%s" % (action, self.profile_name)
