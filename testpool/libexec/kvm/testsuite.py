# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
"""
Tests KVM API

In order to run these tests, either:
  - change the TEST_HOST global variable to your hypervisor and create
    a test.template resource.
  - Use existing CONNECTION and use a localhost KVM hypvervisor and
    create a test.template resource.
Also, make sure tpl-daemon is NOT running.
"""

import time
import unittest
import logging
import libvirt
from testpooldb import models
from testpool.libexec import kvm
from testpool.core import server
from testpool.core import ext
from testpool.core import algo

CONNECTION = "qemu:///system"
TEST_POOL = "test.kvm.pool"
TEMPLATE = "test.template"
PRODUCT = "kvm"


class Testsuite(unittest.TestCase):
    """ tests various aspects of cloning a resource. """

    def setUp(self):
        """ Create KVM pool. """

        (host1, _) = models.Host.objects.get_or_create(
            connection=CONNECTION, product=PRODUCT)
        defaults = {"resource_max": 3, "template_name": TEMPLATE}
        models.Pool.objects.update_or_create(name=TEST_POOL, host=host1,
                                             defaults=defaults)

    def tearDown(self):
        """ Remove any previous test pools1. """

        try:
            pool1 = models.Pool.objects.get(name=TEST_POOL)
            for rsrc in models.Resource.objects.filter(pool=pool1):
                rsrc.delete()
            pool1.delete()
        except models.Pool.DoesNotExist:
            pass

        try:
            host1 = models.Host.objects.get(connection=CONNECTION,
                                            product=PRODUCT)
            host1.delete()
        except models.Host.DoesNotExist:
            pass

    def test_clone(self):
        """ test clone.

        Clone three resources. """
        count = 2

        host1 = libvirt.open(CONNECTION)
        self.assertTrue(host1)

        pool = kvm.api.Pool(CONNECTION, "test")
        self.assertTrue(pool)
        for item in range(count):
            name = TEMPLATE + ".%d" % item
            try:
                pool.destroy(name)
            except libvirt.libvirtError:
                continue

        names = [item for item in pool.conn.listAllDomains()]
        names = [item.name() for item in names]
        names = [item for item in names if item.startswith(TEMPLATE)]
        for item in range(count):
            name = TEMPLATE + ".%d" % item
            if name not in names:
                logging.debug("creating %s", name)
                pool.clone(TEMPLATE, name)
                pool.start(name)

        for item in range(count):
            name = "%s.%d" % (TEMPLATE, item)
            try:
                pool.destroy(name)
            except libvirt.libvirtError:
                continue

    def test_info(self):
        """ test_info """

        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        self.assertTrue(hndl.getInfo())
        self.assertTrue(hndl.getHostname())

    def test_storage(self):
        """ test_storage """
        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        for item in hndl.listDomainsID():
            dom = hndl.lookupByID(item)
            print "Active: Name: ", dom.name()
            print "Active: Info: ", dom.info()

    def test_destroy_missing(self):
        """ test_destroy_missing. """

        pool1 = models.Pool.objects.get(name=TEST_POOL)

        host1 = kvm.api.pool_get(pool1)
        self.assertTrue(host1)

        hndl = libvirt.open(CONNECTION)
        self.assertTrue(hndl)

        try:
            name = "%s.destroy" % TEMPLATE
            host1.start(name)
        except libvirt.libvirtError:
            pass


# pylint: disable=R0903
class FakeArgs(object):
    """ Used in testing to pass values to server.main. """
    def __init__(self):
        self.count = 200
        self.sleep_time = 1
        self.max_sleep_time = 60
        self.min_sleep_time = 1
        self.setup = True
        self.verbose = 0
        self.cfg_file = ""


class TestsuiteServer(unittest.TestCase):
    """ Test model output. """

    def tearDown(self):
        """ Make sure pool is removed. """
        try:
            host1 = models.Host.objects.get(connection=CONNECTION,
                                            product=PRODUCT)
            pool1 = models.Pool.objects.get(name=TEST_POOL, host=host1)
            pool = kvm.api.pool_get(pool1)
            algo.destroy(pool, pool1)

            pool1.delete()
        except models.Host.DoesNotExist:
            pass
        except models.Pool.DoesNotExist:
            pass

    def test_setup(self):
        """ test_setup. """

        (host1, _) = models.Host.objects.get_or_create(connection=CONNECTION,
                                                       product=PRODUCT)

        defaults = {"resource_max": 1, "template_name": TEMPLATE}
        (pool1, _) = models.Pool.objects.update_or_create(
            name=TEST_POOL, host=host1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        self.assertEqual(pool1.resource_set.all().count(), 1)

    def test_shrink(self):
        """ test_shrink. test when the pool shrinks. """

        (host1, _) = models.Host.objects.get_or_create(connection=CONNECTION,
                                                       product=PRODUCT)
        defaults = {"resource_max": 3, "template_name": TEMPLATE}
        (pool1, _) = models.Pool.objects.update_or_create(
            name=TEST_POOL, host=host1, defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        ##
        # Now shrink the pool to two
        pool1.resource_max = 2
        logging.debug("shrinking pool to %d", pool1.resource_max)
        pool1.save()
        ##

        args = FakeArgs()
        args.setup = False
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        exts = ext.api_ext_list()
        logging.debug("process resource size")

        pool = exts[PRODUCT].pool_get(pool1)
        self.assertEqual(len(pool.list(pool1)), 2)

    def test_expand(self):
        """ test_expand. Check when pool increases. """

        (host1, _) = models.Host.objects.get_or_create(connection=CONNECTION,
                                                       product=PRODUCT)
        defaults = {"resource_max": 2, "template_name": TEMPLATE}
        (pool1, _) = models.Pool.objects.update_or_create(
            name=TEST_POOL, host=host1, defaults=defaults)

        ##
        # Now expand to 3
        pool1.resource_max = 3
        pool1.save()
        ##

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        exts = ext.api_ext_list()
        pool = exts[PRODUCT].pool_get(pool1)
        self.assertEqual(len(pool.list(pool1)), 3)

    def test_expiration(self):
        """ test_expiration. """

        resource_max = 3

        (host1, _) = models.Host.objects.get_or_create(connection=CONNECTION,
                                                       product=PRODUCT)
        defaults = {"resource_max": resource_max, "template_name": TEMPLATE}
        (pool1, _) = models.Pool.objects.update_or_create(name=TEST_POOL,
                                                          host=host1,
                                                          defaults=defaults)

        args = FakeArgs()
        server.args_process(args)
        self.assertEqual(server.main(args), 0)

        rsrcs = pool1.resource_set.filter(status=models.Resource.READY)
        self.assertEqual(len(rsrcs), resource_max)

        rsrc = rsrcs[0]

        ##
        # Acquire for 3 seconds.
        rsrc.transition(models.Resource.RESERVED, algo.ACTION_DESTROY, 3)
        time.sleep(5)
        args.setup = False
        args.count = 2
        args.sleep_time = 1
        args.max_sleep_time = 1
        args.min_sleep_time = 1
        server.args_process(args)
        self.assertEqual(server.main(args), 0)
        ##

        exts = ext.api_ext_list()
        server.adapt(exts)

        rsrcs = pool1.resource_set.filter(status=models.Resource.READY)

        ##
        # Check to see if the expiration happens.
        self.assertEqual(rsrcs.count(), 2)
        ##


if __name__ == "__main__":
    unittest.main()
