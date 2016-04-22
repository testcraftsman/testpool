import unittest
import libvirt
import logging
from testpool.libexec import kvm

TEST_HOST="192.168.0.27"

def request_cred(credentials, user_data):
    for credential in credentials:
        if credential[0] == libvirt.VIR_CRED_AUTHNAME:
            credential[4] = "mhamilton"
        elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
            credential[4] = "password"
    return 0

class Testsuite(unittest.TestCase):

    def test_clone(self):
        """ test clone """

        fmt = "qemu+ssh://mhamilton@%s/system"
        connect = fmt % TEST_HOST
        kvm.destroy(connect, "kvm10")
        kvm.clone(connect, "template", "kvm10")

    def test_info(self):
        """ test_info """
        fmt = "qemu+ssh://mhamilton@%s/system"
        cmd = fmt % TEST_HOST
        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)

        self.assertTrue(hndl.getInfo())
        self.assertTrue(hndl.getHostname())

    def test_storage(self):
        """ test_storage """
        fmt = "qemu+ssh://mhamilton@%s/system"
        cmd = fmt % TEST_HOST
        hndl = libvirt.open(cmd)
        self.assertTrue(hndl)
        for item in hndl.listDefinedDomains():
            print "VM: defined", item

        for item in hndl.listDomainsID():
            dom = hndl.lookupByID(item)
            print "Active: Name: ", dom.name()
            print "Active: Info: ", dom.info()

    def btest_auth(self):
        fmt = "qemu+tcp://%s/system"
        cmd = fmt % TEST_HOST
        auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                request_cred, None]
        hndl = libvirt.openAuth(cmd, auth, 0)
        self.assertTrue(hndl)
        hndl.close()

if __name__ == "__main__":
    unittest.main()
