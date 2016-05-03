"""
API for KVM hypervisors.
"""
import logging
from xml.etree import ElementTree
import libvirt
import virtinst.CloneManager as clmgr
import virtinst.cli as cli
from virtinst.User import User


cli.setupGettext()


def get_clone_diskfile(design):
    """ Define clone's disk file. """

    newidx = 0
    for origdev in design.original_devices:
        disk = clmgr.generate_clone_disk_path(origdev, design)
        logging.debug("cloning disk %s to %s", origdev, disk)
        if origdev is None:
            devpath = None
        else:
            devpath = disk

        design.clone_devices = devpath
        newidx += 1


STATES = {
    libvirt.VIR_DOMAIN_NOSTATE: 'no state',
    libvirt.VIR_DOMAIN_RUNNING: 'running',
    libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
    libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
    libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
    libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
    libvirt.VIR_DOMAIN_CRASHED: 'crashed',
}


def vm_state_to_str(dom):
    """ Return string form of state. """

    state = dom.info()[0]
    return '%s is %s,' % (dom.name(), STATES.get(state, state))


class VMPool(object):
    """ Interface to KVM Pool manager. """
    def __init__(self, url_name):
        """ Constructor. """
        self.url_name = url_name
        self.conn = cli.getConnection(url_name)

    def destroy(self, vm_name):
        """ Destroy VM.

        Shutdown the VM if necessary.
        """
        logging.debug("%s vm_destroy", vm_name)

        vm_hndl = self.conn.lookupByName(vm_name)
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

    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        cli.earlyLogging()
        cli.setupLogging("virt-clone", False, False)

        if not User.current().has_priv(User.PRIV_CLONE, self.conn.getURI()):
            cli.fail(("Must be privileged to clone KVM guests"))

        design = clmgr.CloneDesign(conn=self.conn)
        design.clone_name = new_name
        design.original_guest = orig_name

        design.clone_running = False
        design.replace = False
        design.clone_sparse = True
        design.preserve = True

        # This determines the devices that need to be cloned, so that
        # get_clone_diskfile knows how many new disk paths it needs
        design.setup_original()

        get_clone_diskfile(design)

        # setup design object
        design.setup_clone()

        # start cloning
        clmgr.start_duplicate(design)
        logging.debug("end clone")

    def start(self, vm_name):
        """ Start VM. """

        vm_dom = self.conn.lookupByName(vm_name)
        vm_dom.create()


def vmpool_get(url_name):
    """ Return a handle to the KVM API. """
    return VMPool(url_name)
