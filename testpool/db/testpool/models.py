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
   Test schema for tracking tests and their results.
"""
from django.utils import timezone
from django.db import models


# pylint: disable=E1101
class Key(models.Model):
    """ Identifies an associated list of values.

    For example, the key product could have the values ipod, ipad and walkman.
    The set of values are stored in the Values table.
    """

    CONFIG_TYPE_ANY = 0
    CONFIG_TYPE_STRICT = 1

    CONFIG_TYPE = {
        (CONFIG_TYPE_ANY, "ANY"),
        (CONFIG_TYPE_STRICT, "STRICT")
    }

    value = models.CharField(max_length=128, unique=True)
    config_type = models.IntegerField(choices=CONFIG_TYPE, default=0)

    @staticmethod
    def str_to_config_type(value):
        """ Return config_type given string. """
        for (config_type, config_str) in Key.CONFIG_TYPE:
            if value == config_str:
                return config_type
        raise ValueError("unknown: config_type %s", value)

    def __str__(self):
        """ Return testsuite name. """
        return str(self.value)


class KVP(models.Model):
    """ Key-Value Pair associate a key with a set of values. """

    key = models.ForeignKey(Key)
    value = models.CharField(max_length=128)

    def __str__(self):
        """ Return testsuite name. """
        return "%s=%s" % (self.key, self.value)

    @staticmethod
    def get(key, value):
        """ Retrieve KVP. """
        (key, _) = Key.objects.get_or_create(value=key)
        return KVP.objects.get(key=key, value=value)

    @staticmethod
    def get_or_create(key, value):
        """ Create a single test key objects. """

        (key, _) = Key.objects.get_or_create(value=key)

        try:
            testkey = KVP.objects.get(key=key, value=value)
            if testkey:
                return (testkey, False)
        except KVP.DoesNotExist:
            pass

        if key.config_type != Key.CONFIG_TYPE_ANY:
            raise KVP.DoesNotExist("key %s is strict" % key)
        return KVP.objects.get_or_create(key=key, value=value)

    @staticmethod
    def filter(contains):
        """ Filter testsuite against a single string. """

        if not contains:
            return KVP.objects.all()

        return KVP.objects.filter(
            models.Q(key__value__contains=contains) |
            models.Q(value__contains=contains))


class VM(models.Model):
    """ A single test consisting of one or more results. """

    FREE = 2
    RESERVED = 1
    RELEASED = 0

    profile = models.ForeignKey("Profile", null=True, blank=True, default=None)
    name = models.CharField(max_length=128)
    status = models.IntegerField(default=RESERVED, blank=True, null=True)
    reserved = models.DateField(auto_now_add=True)
    expiration = models.IntegerField(default=10*60*60)

    def __str__(self):
        """ User representation. """
        return "%s" % self.name

    @staticmethod
    def status_to_str(status, short=False):
        """ Return string form of the status code. """
        if status == Test.RESERVED:
            return "reserved"
        elif status == Test.RELEASED:
            return "released"
        elif status == Test.FREE:
            return "free"

    @staticmethod
    def status_map(status):
        """ Return status. """
        if status == "reserved":
            return Test.RESERVeD
        elif status == "released":
            return Test.RELEASED


    @staticmethod
    def get_or_create(profile, name):
        """ Get or create reserved VM. """

        ##
        # \todo should be pulled out.
        (name, created) = TestName.objects.get_or_create(name=name)

        ##
        # Look for test.
        vm1 = VM.objects.get(profile=profile, name=name)
        test = Test.objects.create(testsuite=testsuite, name=name,
                                   status=status)

        for key in keys:
            TestKVP.objects.create(test=test, testkey=key)

        return (test, True)


class ProfileKVP(models.Model):
    """ Testsuites are associated to a set of keys. """
    profile = models.ForeignKey("Profile")
    kvp = models.ForeignKey(KVP)

    def __str__(self):
        """ User representation. """
        return "%s %s" % (str(self.testsuite.context), str(self.kvp))


class Profile(models.Model):
    """ A Testsuite holds a set of tests. """

    name = models.CharField(max_length=128, unique=True)
    hv = models.ForeignKey("HV")
    template_name = models.CharField(max_length=128)
    kvps = models.ManyToManyField(KVP, through="ProfileKVP")
    vm_max = models.IntegerField(default=1)

    def __str__(self):
        """ User representation. """

        return str(self.name)

    def kvp_get_or_create(self, kvp):
        """ Add kvp to profile. """
        return self.profilekvp_set.get_or_create(kvp=kvp)


    def kvp_value_get(self, key, default=None):
        """ Return value given key. """
        try:
            kvp = self.profilekvp_set.get(kvp__key__value=key)
            return kvp.kvp.value
        except ProfileKVP.DoesNotExist:
            return default


class HV(models.Model):
    """ A test plan consists of a set of testsuites, tests.
    A test plan governs which testsuites should be run.
    """
    hostname = models.CharField(max_length=128, unique=True)
    product = models.CharField(max_length=128, unique=True)

    def __str__(self):
        """ User representation. """
        return "%s.%s" % (self.product, self.name)