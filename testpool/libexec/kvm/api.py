"""
API for KVM hypervisors.
"""
import sys
import logging
import libvirt
import virtinst.CloneManager as clmgr
import urlgrabber.progress as progress
from xml.etree import ElementTree

import virtinst.cli as cli
from virtinst.User import User

cli.setupGettext()

def get_clone_diskfile(new_diskfiles, design, conn, preserve=False,
                       auto_clone=False):
    """ Define clone's disk file. """
    if new_diskfiles is None:
        new_diskfiles = [None]

    conn = design.original_conn

    newidx = 0
    for origdev in design.original_devices:
        if len(new_diskfiles) <= newidx:
            # Extend the new/passed paths list with None if it's not
            # long enough
            new_diskfiles.append(None)
        disk = new_diskfiles[newidx]

        if disk is None and auto_clone:
            disk = clmgr.generate_clone_disk_path(origdev, design)

        if origdev is None:
            devpath = None
        else:
            dev = check_disk(conn, disk, origdev, preserve)
            devpath = dev.path

        design.clone_devices = devpath
        newidx += 1

def check_disk(conn, clone_path, orig_path, preserve):
    """ Check disk. """

    prompt_txt = (_("What would you like to use as the cloned disk "
                    "(file path) for '%s'?") % orig_path)

    return cli.disk_prompt(conn, clone_path, .00001, False,
                           prompt_txt,
                           warn_overwrite=not preserve,
                           check_size=False,
                           path_to_clone=orig_path)

def get_clone_sparse(sparse, design):
    """ Get clone sparse. """
    design.clone_sparse = sparse

def get_preserve(preserve, design):
    """ Get clone preserve. """
    design.preserve = preserve

states = {
    libvirt.VIR_DOMAIN_NOSTATE: 'no state',
    libvirt.VIR_DOMAIN_RUNNING: 'running',
    libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
    libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
    libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
    libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
    libvirt.VIR_DOMAIN_CRASHED: 'crashed',
}

def vm_state(dom):
    state = dom.info()[0]
    return '%s is %s,' % (dom.name(), states.get(state, state))

class Options(object):
    """ Clone Options. """
    def __init__(self):
        self.clone_running = False
        self.quiet = False
        self.debug = False
        self.replace = False
        self.preserve = True
        self.sparse = True
        self.new_diskfile = []

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
        logging.debug("%s vm_destroy VM state %s", vm_name, vm_state(vm_hndl))
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


    ### Let's do it!
    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        options = Options()

        cli.earlyLogging()

        cli.setupLogging("virt-clone", options.debug, options.quiet)

        if not User.current().has_priv(User.PRIV_CLONE, self.conn.getURI()):
            cli.fail(_("Must be privileged to clone KVM guests"))

        design = clmgr.CloneDesign(conn=self.conn)
        design.clone_name = new_name
        design.original_guest = orig_name

        design.clone_running = options.clone_running
        design.replace = bool(options.replace)

        get_clone_sparse(options.sparse, design)
        get_preserve(options.preserve, design)

        # This determines the devices that need to be cloned, so that
        # get_clone_diskfile knows how many new disk paths it needs
        design.setup_original()

        get_clone_diskfile(options.new_diskfile, design, self.conn,
                           not options.preserve, True)

        # setup design object
        design.setup_clone()

        # start cloning
        meter = progress.TextMeter(fo=sys.stdout)
        clmgr.start_duplicate(design, meter)
        logging.debug("end clone")

    def start(self, vm_name):
        """ Start VM. """

        vm_dom = self.conn.lookupByName(vm_name)
        vm_dom.create()


def vmpool_get(url_name):
    """ Return a handle to the KVM API. """
    return VMPool(url_name)
