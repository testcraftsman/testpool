"""
API for KVM hypervisors.
"""
import docker
import libvirt
import testpool.core.api
from testpool.core import exceptions
from testpool.core import logger

LOGGER = logger.create()


class HostInfo(testpool.core.api.HostInfo):
    """ Hold container information. """
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, info):
        testpool.core.api.HostInfo.__init__(self)
        self.model = str(info[0])
        self.memory_size = info[1]
        self.cpus = info[2]
        self.cpu_mhz = info[3]
        self.numa_nodes = info[4]
        self.cpu_sockets = info[5]
        self.cores_per_socket = info[6]
        self.threads_per_core = info[7]


class Pool(testpool.core.api.Pool):
    """ Interface to KVM Pool manager. """

    # pylint: disable=no-self-use

    def __init__(self, url_name, context):
        """ Constructor. """

        testpool.core.api.Pool.__init__(self, context)

        self.context = context
        self.url_name = url_name
        self.conn = docker.from_env()

    def new_name_get(self, template_name, index):
        """ Given a profile and index, return a new container name. """

        base_name = template_name.split(":")[0]
        return base_name + ".%d" % index

    def timing_get(self, request):
        """ Return algorithm timing based on the request. """

        if request == testpool.core.api.Pool.TIMING_REQUEST_DESTROY:
            return 60
        else:
            raise ValueError("unknown timing request %s" % request)

    def type_get(self):
        """ Return the type of the interface. """

        return "docker"

    def state_get(self, name):
        """ Return the state of the resource. """

        LOGGER.debug("%s: state_get", name)

        try:
            cntnr = self.conn.containers.get(name)
            if cntnr.status == "running":
                return testpool.core.api.Pool.STATE_RUNNING
            return testpool.core.api.Pool.STATE_BAD_STATE
        except docker.errors.NotFound:
            return testpool.core.api.Pool.STATE_NONE

    def destroy(self, name):
        """ Destroy container.

        return api.Pool.STATE_NONE When container name does not exist.
        """

        LOGGER.debug("%s destroy", name)
        try:
            cntnr = self.conn.containers.get(name)
            cntnr.remove(v=True, force=True)
            return testpool.core.api.Pool.STATE_DESTROYED
        except docker.errors.NotFound:
            LOGGER.debug("container %s does not exist", name)
            return testpool.core.api.Pool.STATE_NONE

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        self.conn.images.pull(orig_name)
        self.conn.containers.create(orig_name, detach=True, name=new_name)
        LOGGER.debug("%s: cloned", new_name)

    def start(self, name):
        """ Start container. """

        try:
            cntnr = self.conn.containers.get(name)
            cntnr.start()
            LOGGER.debug("%s started", name)
            return testpool.core.api.Pool.STATE_RUNNING
        except docker.errors.APIError:
            LOGGER.error("%s failed to start", name)
            return testpool.core.api.Pool.STATE_BAD_STATE

    # pylint: disable=unused-argument
    def ip_get(self, name, source=0):
        """ Return IP address of resource.

        IP address may not be found if the resource is not fully running.
        """

        LOGGER.debug("%s: ip_get called", name)
        api = docker.APIClient()
        info = api.inspect_container(name)

        try:
            return info["NetworkSettings"]["IPAddress"]
        except KeyError:
            return None

    def list(self, profile1):
        """ Return the list of resources. """

        filters = {"ancestor":  profile1.template_name}
        cntnrs = self.conn.containers.list(filters=filters)
        return [item.name for item in cntnrs]

    # pylint: disable=W0613
    # pylint: disable=R0201
    def resource_attr_get(self, name):
        """ Return the list of attributes for the resource.

        These attributes are stored in the database, eventually they are
        passed through the REST interface to the client.
        """

        return {}

    def is_clone(self, profile1, name):
        """ Return True if vm1 is a clone of profile1 template. """

        return (name.startswith(profile1.template_name) and
                name != profile1.template_name)

    def info_get(self):
        """ Return information about the hypervisor profile. """

        host_info = self.conn.getInfo()

        ret_value = HostInfo(host_info)
        return ret_value


def pool_get(profile):
    """ Return a handle to the KVM API. """
    try:
        return Pool(profile.hv.connection, profile.name)
    except libvirt.libvirtError, arg:
        # LOGGER.exception(arg)
        raise exceptions.ProfileError(str(arg), profile)
