# (c) 2015 Mark Hamilton, <mark.lee.hamilton@gmail.com>
#
# This file is part of testbed
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
from django.test import TestCase
from .models import Profile
from .models import Key
from .models import KVP
from .models import HV
from .models import VM


class ModelTestCase(TestCase):
    """ Test model output. """

    def test_profile(self):
        """ test_profile. """

        key1 = Key.objects.create(value="key1")
        key2 = Key.objects.create(value="key2")
        kvps = (KVP.objects.create(key=key1, value="value1"),
                KVP.objects.create(key=key2, value="value2"))

        hv1 = HV.objects.create(hostname="localhost")

        profile1 = Profile.objects.create(name="profile1", hv=hv1, vm_max=3,
                                          template_name="template.ubuntu1404")
        for kvp in kvps:
            profile1.kvp_get_or_create(kvp)

        self.assertEqual(profile1.kvp_value_get("key1"), "value1")
        self.assertEqual(profile1.kvp_value_get("key2"), "value2")

    def test_vm(self):
        """ Generate several VM instances. """

        hv1 = HV.objects.create(hostname="localhost")
        self.assertTrue(hv1)

        profile1 = Profile.objects.create(name="profile1", hv=hv1, vm_max=3,
                                          template_name="template.ubuntu1404")
        self.assertTrue(profile1)

        for item in range(3):
            vm1 = VM.objects.create(profile=profile1,
                                    name="template.ubuntu1404.%d" % item,
                                    status=VM.FREE,
                                    expiration=10*60*60*10000000)
            self.assertTrue(vm1)
