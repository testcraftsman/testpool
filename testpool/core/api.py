# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
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
    TIMING_REQUEST_ATTR = "timing.request.attr"
    TIMING_REQUEST_CLONE = "timing.request.clone"
    TIMING_REQUEST_NONE = "timing.request.none"

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
        """ Given a pool, generate a new name. """

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
        """ Return the current name. """
        raise NotImplementedError(NOT_IMPL % "state_get")

    def is_clone(self, pool1, name):
        """ Return True if resource is a clone for the pool1. """

        raise NotImplementedError(NOT_IMPL % "is_clone")

    def list(self, pool1):
        """ Return the list of resources for the pool1. """
        raise NotImplementedError(NOT_IMPL % "list")
