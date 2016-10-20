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
""" VM Pool API. """


class VMPool(object):
    """ VM Pool API. """

    TIMING_REQUEST_DESTROY = "timing.request.destroy"

    STATE_RUNNING = 1
    """ The VM is running. """
    STATE_NONE = 2
    """ Indicate that the VM does not exist. """

    STATE_BAD_STATE = 3
    """ System exists but is not running. """

    STATE_DESTROYED = 4
    """ VM has been destroyed. """

    STATE_STRING = {
        STATE_RUNNING: "running",
        STATE_NONE: "none",
        STATE_BAD_STATE: "badstate"
        }

    def __init__(self, context):
        self.context = context

    def timing_get(self, request):
        """ Return the time in seconds for the request. """
        raise NotImplementedError("timing_get unsupported")

    def type_get(self):
        """ Return the pool type. """
        raise NotImplementedError("type_get unsupported")

    def clone(self, orig_name, new_name):
        """ Clone orig_name to new_name. """
        raise NotImplementedError("clone unsupported")

    def start(self, vm_name):
        """ Start vm_name VM. """
        raise NotImplementedError("start unsupported")

    def vm_state_get(self, vm_name):
        """ Return the current vm_name. """
        raise NotImplementedError("state_get unsupported")

    def vm_list(self):
        """ Return the list of VMs. """
        raise NotImplementedError("state_list unsupported")
