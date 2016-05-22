class VMPool(object):
    STATE_RUNNING = 1
    """ The VM is running. """
    STATE_NONE = 2
    """ Indicate that the VM does not exist. """
    STATE_BAD_STATE = 3
    """ System exists but is not running. """

    def __init__(self, context):
        self.context = context

    def type_get(self):
        raise Unsupported("type_get unsupported")

    def clone(self, orig_name, new_name):
        raise Unsupported("clone unsupported")

    def start(self, vm_name):
        raise Unsupported("start unsupported")
    
    def vm_state_get(self, vm_name):
        raise Unsupported("state_get unsupported")

    def profile_mark_bad(self, profile_name):
        raise Unsupported("profile_mark_bad %s unsupported" % vm_name)
