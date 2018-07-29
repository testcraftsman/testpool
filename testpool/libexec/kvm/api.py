"""
API for KVM hypervisors.
"""
import sys
import os
from xml.etree import ElementTree
import libvirt
import testpool.core.api
from testpool.core import exceptions
from testpool.core import logger

LOGGER = logger.create()


##
# Because KVM support is bunbled with testpool, we do not want to
# fail if the intent is to not use it.
# pylint: disable=E0401
try:
    import virtinst.cloner as cloner
    import virtinst.connection
except ImportError:
    VIRTINST_DIR = os.path.join("/usr", "share", "virt-manager")
    if os.path.exists(VIRTINST_DIR) and VIRTINST_DIR not in sys.path:
        sys.path.append(VIRTINST_DIR)
        import virtinst.cloner as cloner
        import virtinst.connection
# pylint: enable=E0401
##


##
# pylint: disable=W0613
def libvirt_callback(userdata, err):
    """ libvirt callback to address exceptions. """
    pass
# pylint: enable=W0613
##


libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


def get_clone_diskfile(design):
    """ Retrieve disk content for cloning. """

    new_diskfiles = [None]
    newidx = 0
    clonepaths = []
    for origpath in [d.path for d in design.original_disks]:
        if len(new_diskfiles) <= newidx:
            # Extend the new/passed paths list with None if it's not
            # long enough
            new_diskfiles.append(None)
        newpath = new_diskfiles[newidx]

        if newpath is None:
            newpath = design.generate_clone_disk_path(origpath)

        if origpath is None:
            newpath = None

        LOGGER.debug("cloning disk %s to %s", origpath, newpath)
        clonepaths.append(newpath)
        newidx += 1
    design.clone_paths = clonepaths

    for disk in design.clone_disks:
        _, errmsg = disk.is_size_conflict()
        # The isfatal case should have already caused us to fail
        if errmsg:
            LOGGER.warning("disk size limit exceeded")


def vm_state_to_str(dom):
    """ Return string form of state. """

    states = {
        libvirt.VIR_DOMAIN_NOSTATE: 'no state',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
        libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
    }

    state = dom.info()[0]
    return '%s is %s,' % (dom.name(), states.get(state, state))


class HostInfo(testpool.core.api.HostInfo):
    """ Holds Host information. """
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self, kvm_info):
        testpool.core.api.HostInfo.__init__(self)
        self.model = str(kvm_info[0])
        self.memory_size = kvm_info[1]
        self.cpus = kvm_info[2]
        self.cpu_mhz = kvm_info[3]
        self.numa_nodes = kvm_info[4]
        self.cpu_sockets = kvm_info[5]
        self.cores_per_socket = kvm_info[6]
        self.threads_per_core = kvm_info[7]


class Pool(testpool.core.api.Pool):
    """ Interface to KVM Pool manager. """

    # pylint: disable=no-self-use

    def __init__(self, url_name, context):
        """ Constructor. """

        testpool.core.api.Pool.__init__(self, context)

        self.context = context
        self.url_name = url_name
        if url_name.startswith("qemu+tcp"):
            auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                    None]
            self.conn = libvirt.openAuth(url_name, auth, 0)
        elif url_name.startswith("qemu") or url_name.startswith("qemu+ssh"):
            self.conn = libvirt.open(url_name)
        else:
            raise ValueError("unsupported connection %s" % url_name)

    def new_name_get(self, template_name, index):
        """ Given a profile, generate a new name. """
        name = template_name + ".%d" % index
        return name

    def timing_get(self, request):
        """ Return algorithm timing based on the request. """

        if request == testpool.core.api.Pool.TIMING_REQUEST_DESTROY:
            return 60
        else:
            raise ValueError("unknown timing request %s" % request)

    def type_get(self):
        """ Return the type of the interface. """
        return "kvm"

    def state_get(self, name):
        """ Return the state of the resource. """

        try:
            vm_hndl = self.conn.lookupByName(name)
            return vm_hndl.info()[0]
        except libvirt.libvirtError:
            return testpool.core.api.Pool.STATE_NONE

    def destroy(self, name):
        """ Destroy resource.

        Shutdown the resource if necessary.
        """

        LOGGER.debug("%s resource_destroy", name)
        try:
            vm_hndl = self.conn.lookupByName(name)
        except (AttributeError, libvirt.libvirtError):
            return testpool.core.api.Pool.STATE_NONE

        LOGGER.debug("%s resource_destroy resource state %s", name,
                     vm_state_to_str(vm_hndl))
        vm_xml = vm_hndl.XMLDesc()

        root = ElementTree.fromstring(vm_xml)
        disk_source = root.find("./devices/disk/source")
        volume_in_use = str(disk_source.get("file"))

        [state, _, _, _, _] = vm_hndl.info()
        if state != libvirt.VIR_DOMAIN_SHUTOFF:
            LOGGER.debug("%s destroy resource", name)
            vm_hndl.destroy()

        [state, _, _, _, _] = vm_hndl.info()
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            LOGGER.debug("%s undefine resource", name)
            vm_hndl.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE)

        LOGGER.debug("%s destroy volume %s", name, volume_in_use)
        vm_vol = self.conn.storageVolLookupByPath(volume_in_use)
        vm_vol.wipe(0)
        vm_vol.delete(0)
        return testpool.core.api.Pool.STATE_DESTROYED

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        def _do_creds_authname(_):
            return 0

        self.conn = virtinst.connection.VirtualConnection(self.url_name)
        self.conn.open(_do_creds_authname)

        design = cloner.Cloner(self.conn)

        design.clone_running = False
        design.replace = True
        design.clone_macs = None
        design.clone_sparse = True
        design.preserve = True

        design.clone_name = new_name
        design.original_guest = orig_name

        # This determines the devices that need to be cloned, so that
        # get_clone_diskfile knows how many new disk paths it needs
        design.setup_original()
        get_clone_diskfile(design)

        # setup design object
        design.setup_clone()
        # start cloning
        design.start_duplicate(None)
        LOGGER.debug("end clone")

    def start(self, name):
        """ Start resource. """

        vm_dom = self.conn.lookupByName(name)
        rtc = vm_dom.create()

        if rtc == 0:
            return testpool.core.api.Pool.STATE_RUNNING
        return testpool.core.api.Pool.STATE_BAD_STATE

    def ip_get(self, name, source=0):
        """ Return IP address of resource.

        IP address may not be found if the resource is not fully running.
        """
        LOGGER.debug("%s: ip_get called", name)

        try:
            dom = self.conn.lookupByName(name)
            LOGGER.debug("%s: ip_get dom %s", name, dom)
        except libvirt.libvirtError:
            return None

        try:
            LOGGER.debug("%s: domain not found", name)
            ifc = dom.interfaceAddresses(0)
            LOGGER.debug("%s: ip_get dom ifc %s", name, ifc)
        except libvirt.libvirtError:
            return None

        try:
            for (_, values) in ifc.iteritems():
                return values["addrs"][source]["addr"]
        except KeyError:
            LOGGER.debug("%s: ip address not set", name)
        return None

    def list(self, profile1):
        """ Return the list of resources. """

        rtc = []

        for item in self.conn.listAllDomains():
            name = item.name()
            if self.is_clone(profile1, name):
                rtc.append(name)
        return rtc

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
    ##
    # User qemu+ssh://hostname/system list --all
    # or
    # User qemu+tcp://username@hostname/system list --all
    try:
        return Pool(profile.host.connection, profile.name)
    except libvirt.libvirtError, arg:
        # LOGGER.exception(arg)
        raise exceptions.ProfileError(str(arg), profile)
