import sys
import logging
import virtinst.CloneManager as clmgr
import urlgrabber.progress as progress
from xml.etree import ElementTree

import optparse
from optparse import OptionGroup
import virtinst.cli as cli
from virtinst.cli import fail, print_stdout, print_stderr
from virtinst.User import User

cli.setupGettext()


def get_clone_diskfile(new_diskfiles, design, conn, preserve=False,
                       auto_clone=False):
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
            dev = _check_disk(conn, disk, origdev, preserve)
            devpath = dev.path

        design.clone_devices = devpath
        newidx += 1

def _check_disk(conn, clone_path, orig_path, preserve):

    prompt_txt = (_("What would you like to use as the cloned disk "
                    "(file path) for '%s'?") % orig_path)

    return cli.disk_prompt(conn, clone_path, .00001, False,
                           prompt_txt,
                           warn_overwrite=not preserve,
                           check_size=False,
                           path_to_clone=orig_path)

def get_clone_sparse(sparse, design):
    design.clone_sparse = sparse

def get_preserve(preserve, design):
    design.preserve = preserve


class Options(object):
    def __init__(self):
        self.clone_running = False
        self.quiet = False
        self.debug = False
        self.replace = False
        self.preserve = True
        self.sparse = True
        self.new_diskfile = []

class VMPool(object):
    def __init__(self, url_name):
        self.url_name = url_name
        self.conn = cli.getConnection(url_name)

    def destroy(self, vm_name):
        """ Destroy VM.
        Shutdown the VM if necessary.
        """
        print "MARK: destroy api"
        logging.debug("vm_destroy VM %s" % vm_name)

        vm_hndl = self.conn.lookupByName(vm_name)
        print "MARK: api 2"
        vm_info = vm_hndl.info()
        if vm_info[0] != 5:
            vm_hndl.shutdown()

        print "MARK: what"
        vm_xml = vm_hndl.XMLDesc(0)
        pool = self.conn.storagePoolLookupByName("default")
        print "MARK: vol", pool
        root = ElementTree.fromstring(vm_xml)
        disk_source = root.find("./devices/disk/source")
        volume_in_use = disk_source.get("file")
        print "MARK: storage", volume_in_use
        vm_hndl.undefine()

        #vm_vol = pool.createXML(vm_xml, 0)
        #vm_vol.wipe(0)
        #vm_vol.delete(0)


    ### Let's do it!
    def clone(self, orig_name, new_name):
        """ Clone KVM system. """

        options = Options()

        cli.earlyLogging()

        cli.setupLogging("virt-clone", options.debug, options.quiet)

        if not User.current().has_priv(User.PRIV_CLONE, self.conn.getURI()):
            fail(_("Must be privileged to clone Xen guests"))

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
