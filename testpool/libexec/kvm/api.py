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

logger = logger.create()


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

        logger.debug("cloning disk %s to %s", origpath, newpath)
        clonepaths.append(newpath)
        newidx += 1
    design.clone_paths = clonepaths

    for disk in design.clone_disks:
        _, errmsg = disk.is_size_conflict()
        # The isfatal case should have already caused us to fail
        if errmsg:
            logger.warning("disk size limit exceeded")


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


class VMPool(testpool.core.api.VMPool):
    """ Interface to KVM Pool manager. """

    def __init__(self, url_name, context):
        """ Constructor. """
        testpool.core.api.VMPool.__init__(self, context)

        self.context = context
        self.url_name = url_name
        if url_name.startswith("qemu") or url_name.startswith("qemu+ssh"):
            self.conn = libvirt.open(url_name)
        elif url_name.startswith("qemu+tcp"):
            auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                    None]
            self.conn = libvirt.openAuth(url_name, auth, 0)

    def timing_get(self, request):
        """ Return algorithm timing based on the request. """

        if request == testpool.core.api.VMPool.TIMING_REQUEST_DESTROY:
            return 60
        else:
            raise ValueError("unknown timing request %s", request)

    def type_get(self):
        """ Return the type of the interface. """
        return "kvm"

    def vm_state_get(self, vm_name):
        """ Return the state of the VM. """

        try:
            vm_hndl = self.conn.lookupByName(vm_name)
            return vm_hndl.info()[0]
        except libvirt.libvirtError:
            return testpool.core.api.VMPool.STATE_NONE

    def destroy(self, vm_name):
        """ Destroy VM.

        Shutdown the VM if necessary.
        """

        logger.debug("%s vm_destroy", vm_name)
        try:
            vm_hndl = self.conn.lookupByName(vm_name)
        except (AttributeError, libvirt.libvirtError):
            return testpool.core.api.VMPool.STATE_NONE

        logger.debug("%s vm_destroy VM state %s", vm_name,
                      vm_state_to_str(vm_hndl))
        vm_xml = vm_hndl.XMLDesc()

        root = ElementTree.fromstring(vm_xml)
        disk_source = root.find("./devices/disk/source")
        volume_in_use = str(disk_source.get("file"))

        [state, _, _, _, _] = vm_hndl.info()
        if state != libvirt.VIR_DOMAIN_SHUTOFF:
            logger.debug("%s destroy VM", vm_name)
            vm_hndl.destroy()

        [state, _, _, _, _] = vm_hndl.info()
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            logger.debug("%s undefine VM", vm_name)
            vm_hndl.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE)

        logger.debug("%s destroy volume %s", vm_name, volume_in_use)
        vm_vol = self.conn.storageVolLookupByPath(volume_in_use)
        vm_vol.wipe(0)
        vm_vol.delete(0)
        return testpool.core.api.VMPool.STATE_DESTROYED

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """
        def _do_creds_authname(_):
            return 0

        conn = virtinst.connection.VirtualConnection(self.url_name)
        conn.open(_do_creds_authname)

        design = cloner.Cloner(conn)

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
        logger.debug("end clone")

    def start(self, vm_name):
        """ Start VM. """

        vm_dom = self.conn.lookupByName(vm_name)
        rtc = vm_dom.create()

        if rtc == 0:
            return testpool.core.api.VMPool.STATE_RUNNING
        else:
            return testpool.core.api.VMPool.STATE_BAD_STATE

    def ip_get(self, vm_name, source=0):
        """ Return IP address of VM.
        IP address may not be found if the VM is not fully running.
        """
        logger.debug("%s: ip_get called", vm_name)

        try:
            dom = self.conn.lookupByName(vm_name)
            logger.debug("%s: ip_get dom %s", vm_name, dom)
        except libvirt.libvirtError:
            return None

        try:
            logger.debug("%s: domain not found", vm_name)
            ifc = dom.interfaceAddresses(0)
            logger.debug("%s: ip_get dom ifc %s", vm_name, ifc)
        except libvirt.libvirtError:
            return None

        try:
            for (_, values) in ifc.iteritems():
                return values["addrs"][source]["addr"]
        except KeyError:
            logger.debug("%s: ip address not set", vm_name)
        return None

    def vm_list(self, profile1):
        """ Return the list of VMs. """

        rtc = []

        for item in self.conn.listAllDomains():
            vm_name = item.name()
            if self.vm_is_clone(profile1, vm_name):
                rtc.append(vm_name)
        return rtc

    # pylint: disable=W0613
    # pylint: disable=R0201
    def vm_attr_get(self, vm_name):
        """ Return the list of attributes for the VM.

        These attributes are stored in the database, eventually they are
        passed through the REST interface to the client.
        """

        return {}

    def vm_is_clone(self, profile1, vm_name):
        """ Return True if vm1 is a clone of profile1 template. """

        return (vm_name.startswith(profile1.template_name) and
                vm_name != profile1.template_name)

    def info_get(self):
        """ Return information about the hypervisor profile. """

        host_info = self.conn.getInfo()

        ret_value = HostInfo(host_info)
        return ret_value
        

def vmpool_get(profile):
    """ Return a handle to the KVM API. """
    ##
    # User qemu+ssh://hostname/system list --all
    # or 
    # User qemu+tcp://username@hostname/system list --all
    try:
        return VMPool(profile.hv.connection, profile.name)
    except libvirt.libvirtError, arg:
        # logger.exception(arg)
        raise exceptions.ProfileError(str(arg), profile)
