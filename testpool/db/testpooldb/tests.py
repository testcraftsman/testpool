# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testpool
#
# Testbed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Testbed is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Testdb.  If not, see <http://www.gnu.org/licenses/>.
"""
  Create your tests here.
"""
import sys

from django.test import TestCase
from .models import Pool
from .models import Key
from .models import KVP
from .models import Host
from .models import Resource
from .models import ResourceKVP


class Testsuite(TestCase):
    """ Test model output. """

    def test_pool(self):
        """ test_pool. """

        key1 = Key.objects.create(value="key1")
        key2 = Key.objects.create(value="key2")
        kvps = (KVP.objects.create(key=key1, value="value1"),
                KVP.objects.create(key=key2, value="value2"))

        host1 = Host.objects.create(connection="localhost")

        pool1 = Pool.objects.create(name="pool1", host=host1, resource_max=3,
                                    template_name="template.ubuntu1404")
        for kvp in kvps:
            pool1.kvp_get_or_create(kvp)

        self.assertEqual(pool1.kvp_value_get("key1"), "value1")
        self.assertEqual(pool1.kvp_value_get("key2"), "value2")

    def test_resource(self):
        """ Generate several resource instances. """

        host1 = Host.objects.create(connection="localhost")
        self.assertTrue(host1)

        pool1 = Pool.objects.create(name="pool1", host=host1, resource_max=3,
                                    template_name="template.ubuntu1404",
                                    expiration=10*60*60*10000000)
        self.assertTrue(pool1)

        for item in range(3):
            name = "template.ubuntu1404.%d" % item
            rsrc1 = Resource.objects.create(pool=pool1, name=name,
                                            status=Resource.PENDING)
            self.assertTrue(rsrc1)

    def test_rsrc_attr(self):
        """ Test adding attribute to a resource. """

        host1 = Host.objects.create(connection="localhost")
        self.assertTrue(host1)

        pool1 = Pool.objects.create(name="pool1", host=host1, resource_max=3,
                                    template_name="template.ubuntu1404",
                                    expiration=10*60*60*10000000)
        self.assertTrue(pool1)

        rsrc = Resource.objects.create(pool=pool1,
                                       name="template.ubuntu1404.0",
                                       status=Resource.PENDING)
        self.assertTrue(rsrc1)
        (kvp, _) = KVP.get_or_create("key1", "value1")
        ResourceKVP.objects.create(vm=rsrc, kvp=kvp)

    def test_exception(self):
        """ Test storing an exception in a pool. """

        host1 = Host.objects.create(connection="localhost")
        self.assertTrue(host1)
        pool1 = Pool.objects.create(name="pool1", host=host1, resource_max=3,
                                    template_name="template.ubuntu1404",
                                    expiration=10*60*60)
        self.assertTrue(pool1)

        try:
            1/0
        except ZeroDivisionError, arg:
            stack_trace = sys.exc_info()[2]
            pool1.stacktrace_set(str(arg), stack_trace)

        levels = pool1.traceback_set.order_by("level")
        self.assertTrue(len(levels), 1)
