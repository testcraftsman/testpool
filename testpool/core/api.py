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
""" Pool API. """


# pylint: disable=R0902
# pylint: disable=R0903
class HostInfo(object):
    """ Basic host information. """
    def __init__(self):
        self.model = None
        self.memory_size = None
        self.cpus = None
        self.cpu_mhz = None
        self.numa_nodes = None
        self.cpu_sockets = None
        self.cores_per_socket = None
        self.threads_per_core = None


NOT_IMPL = "%s not implemented"


class Pool(object):
    """ Pool API. """

    TIMING_REQUEST_DESTROY = "timing.request.destroy"

    STATE_RUNNING = 1
    """ The resource is running. """

    STATE_NONE = 2
    """ Indicate that the resource does not exist. """

    STATE_BAD_STATE = 3
    """ System exists but is not running. """

    STATE_DESTROYED = 4
    """ resource has been destroyed. """

    STATE_STRING = {
        STATE_RUNNING: "running",
        STATE_NONE: "none",
        STATE_BAD_STATE: "badstate",
        STATE_DESTROYED: "destroyed"
    }

    def __init__(self, context):
        self.context = context

    def new_name_get(self, template_name, index):
        """ Given a profile, generate a new name. """

        raise NotImplementedError(NOT_IMPL % "new_name_get")

    def timing_get(self, request):
        """ Return the time in seconds for the request. """
        raise NotImplementedError(NOT_IMPL % "timing_get")

    def type_get(self):
        """ Return the pool type. """
        raise NotImplementedError(NOT_IMPL % "type_get")

    def clone(self, orig_name, new_name):
        """ Clone orig_name to new_name. """
        raise NotImplementedError(NOT_IMPL % "clone")

    def start(self, name):
        """ Start name content. """
        raise NotImplementedError(NOT_IMPL % "start")

    def state_get(self, name):
        """ Return the current vm_name. """
        raise NotImplementedError(NOT_IMPL % "state_get")

    def vm_is_clone(self, profile1, vm_name):
        """ Return True if vm1 is a clone for the profile1. """

        raise NotImplementedError(NOT_IMPL % "vm_is_clone")

    def list(self, profile1):
        """ Return the list of resources for the profile1. """
        raise NotImplementedError(NOT_IMPL % "list")
