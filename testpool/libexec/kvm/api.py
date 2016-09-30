"""
API for KVM hypervisors.
"""
import sys
import os
import logging
from xml.etree import ElementTree
import libvirt
import testpool.core.api

def libvirt_callback(userdata, err):
    ignore = userdata
    ignore = err
libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


##
# Because KVM support is bunbled with testpool, we do not want to
# fail if the intent is to not use it.
try:
    import virtinst.cloner as cloner
    import virtinst.connection
    # from virtinst.User import User
except ImportError:
    virtinst_dir = os.path.join("/usr", "share", "virt-manager")
    if os.path.exists(virtinst_dir) and virtinst_dir not in sys.path:
        sys.path.append(virtinst_dir)
        import virtinst.cloner as cloner
        import virtinst.connection
##


def get_clone_diskfile(design):

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

        logging.debug("cloning disk %s to %s", origpath, newpath)
        clonepaths.append(newpath)
        newidx += 1
    design.clone_paths = clonepaths

    for disk in design.clone_disks:
        _, errmsg = disk.is_size_conflict()
        # The isfatal case should have already caused us to fail
        if errmsg:
            logging.warning("disk size limit exceeded")


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


class VMPool(testpool.core.api.VMPool):
    """ Interface to KVM Pool manager. """

    def __init__(self, url_name, context):
        """ Constructor. """

        self.context = context
        self.url_name = url_name
        self.conn = libvirt.open(url_name)

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

        logging.debug("%s vm_destroy", vm_name)
        try:
            vm_hndl = self.conn.lookupByName(vm_name)
        except (AttributeError, libvirt.libvirtError):
            return testpool.core.api.VMPool.STATE_NONE
            
        logging.debug("%s vm_destroy VM state %s", vm_name,
                      vm_state_to_str(vm_hndl))
        vm_xml = vm_hndl.XMLDesc()

        root = ElementTree.fromstring(vm_xml)
        disk_source = root.find("./devices/disk/source")
        volume_in_use = str(disk_source.get("file"))

        [state, _, _, _, _] = vm_hndl.info()
        if state != libvirt.VIR_DOMAIN_SHUTOFF:
            logging.debug("%s destroy VM", vm_name)
            vm_hndl.destroy()

        [state, _, _, _, _] = vm_hndl.info()
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            logging.debug("%s undefine VM", vm_name)
            vm_hndl.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE)

        logging.debug("%s destroy volume %s", vm_name, volume_in_use)
        vm_vol = self.conn.storageVolLookupByPath(volume_in_use)
        vm_vol.wipe(0)
        vm_vol.delete(0)
        return testpool.core.api.VMPool.STATE_DESTROYED

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """
        def _do_creds_authname(creds):
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
        logging.debug("end clone")

    def start(self, vm_name):
        """ Start VM. """

        vm_dom = self.conn.lookupByName(vm_name)
        vm_dom.create()

    def ip_get(self, vm_name, source=0):
        """ Return IP address of VM. 
        IP address may not be found if the VM is not fully running.
        """

        try:
            dom = self.conn.lookupByName(vm_name)
            ifc = dom.interfaceAddresses(0) 
        except libvirt.libvirtError:
            logging.debug("%s: domain not found", vm_name)
            return None
        try:
            ip_addr = ifc["addrs"][source]["addr"]
            return ip_addr
        except KeyError:
            logging.debug("%s: ip address not set", vm_name)
            return None

    def vm_list(self):
        """ Return the list of VMs. """

        rtc = []

        for item in self.conn.listAllDomains():
            rtc.append(item.name())
        return rtc


def vmpool_get(profile):
    """ Return a handle to the KVM API. """
    context = "%s/%s" % (profile.hv.hostname, profile.name)
    ##
    # User qemu+ssh://hostname/system list --all
    url_name = "qemu+ssh://%s/system" % profile.hv.hostname
    return VMPool(url_name, context)
