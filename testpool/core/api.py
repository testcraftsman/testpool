""" VM Pool API. """


class VMPool(object):
    """ VM Pool API. """

    STATE_RUNNING = 1
    """ The VM is running. """
    STATE_NONE = 2
    """ Indicate that the VM does not exist. """
    STATE_BAD_STATE = 3
    """ System exists but is not running. """

    STATE_STRING = {
        STATE_RUNNING: "running",
        STATE_NONE: "none",
        STATE_BAD_STATE: "badstate"
        }

    def __init__(self, context):
        self.context = context

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
