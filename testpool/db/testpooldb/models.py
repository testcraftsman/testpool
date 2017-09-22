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
   Test schema for tracking tests and their results.
"""
import traceback
import logging
import datetime
from django.db import models

LOGGER = logging.getLogger("testpool.db")


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
        raise ValueError("unknown: config_type %s" % value)

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
        """ Filter against a single string. """

        if not contains:
            return KVP.objects.all()

        return KVP.objects.filter(
            models.Q(key__value__contains=contains) |
            models.Q(value__contains=contains))


class VMKVP(models.Model):
    """ Key value pair for profile. """

    # pylint: disable=C0103
    vm = models.ForeignKey("VM")
    # pylint: enable=C0103
    kvp = models.ForeignKey(KVP)

    def __str__(self):
        """ User representation. """
        return str(self.kvp)


class VM(models.Model):
    """ A single test consisting of one or more results.
    READY - system is ready to be used.
    PENDING - system is pending towards being ready.
    RESERVED - VM is currently in use.
    BAD - VM is in a bad state
    """

    ACTION_DESTROY = "destroy"

    READY = 3
    PENDING = 2
    RESERVED = 1
    BAD = 0

    profile = models.ForeignKey("Profile")
    name = models.CharField(max_length=128)
    status = models.IntegerField(default=PENDING)

    ##
    # ip_addr is the IP address in dot notation
    # xxx.xxx.xxx.xxx
    # This is the IP of the management interface.
    ip_addr = models.CharField(max_length=16, blank=True, null=True)
    ##
    action = models.CharField(max_length=36, default="clone")
    action_time = models.DateTimeField(auto_now_add=True)
    kvps = models.ManyToManyField(KVP, through="VMKVP")

    def __str__(self):
        """ User representation. """
        return str(self.name)

    def release(self):
        """ Acquire VM. """

        self.status = VM.PENDING
        self.save()

    def status_as_str(self):
        """ Return status as string. """
        return VM.status_to_str(self.status)

    @staticmethod
    def status_to_str(status):
        """ Return string form of the status code. """

        if status == VM.RESERVED:
            return "reserved"
        elif status == VM.PENDING:
            return "pending"
        elif status == VM.BAD:
            return "bad"
        elif status == VM.READY:
            return "ready"
        else:
            raise ValueError("status %d unknown" % status)

    @staticmethod
    def status_map(status):
        """ Return status. """
        if status == "reserved":
            return VM.RESERVED
        elif status == "bad":
            return VM.BAD
        elif status == "ready":
            return VM.READY
        elif status == "pending":
            return VM.PENDING
        else:
            raise ValueError("status %s unknown" % status)

    def transition(self, status, action, action_time_delta):
        """ Transition VM through states. """

        LOGGER.info("%s: transition %s to %s in %d (sec)", self.name,
                    VM.status_to_str(status), action, action_time_delta)
        self.status = status
        self.action = action
        delta = datetime.timedelta(seconds=action_time_delta+1)
        self.action_time = datetime.datetime.now() + delta
        self.save()


class Traceback(models.Model):
    """ Holds exception.  """

    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    level = models.IntegerField(default=0, null=True)
    file_name = models.CharField(max_length=128, null=True)
    lineno = models.IntegerField(default=0, null=True)
    func_name = models.CharField(max_length=32, null=True)
    text = models.CharField(max_length=128)

    def __str__(self):
        """ User representation. """

        if self.file_name and self.lineno and self.func_name:
            return "File %s, line %d, in %s\n    %s" % \
                   (self.file_name, self.lineno, self.func_name, self.text)
        return self.text


class ProfileKVP(models.Model):
    """ Key value pair for profile. """

    profile = models.ForeignKey("Profile")
    kvp = models.ForeignKey(KVP)

    def __str__(self):
        """ User representation. """
        return "%s %s" % (str(self.profile), str(self.kvp))


class HV(models.Model):
    """ Hypervisor. """

    connection = models.CharField(max_length=128)
    product = models.CharField(max_length=128)

    def __contains__(self, key):
        """ Return True if srch is in this object. """

        if key in str(self.connection):
            return True
        if key in str(self.product):
            return True
        return False

    def __str__(self):
        """ User representation. """
        return "%s.%s" % (self.product, self.connection)


# pylint: disable=C0103
class Profile(models.Model):
    """ A Testsuite holds a set of tests. """

    READY = 1
    BAD = 0

    name = models.CharField(max_length=128, unique=True)
    hv = models.ForeignKey(HV, on_delete=models.CASCADE)
    template_name = models.CharField(max_length=128)
    kvps = models.ManyToManyField(KVP, through="ProfileKVP")
    vm_max = models.IntegerField(default=1)
    expiration = models.IntegerField(default=10*60)

    status = models.IntegerField(default=READY)

    action = models.CharField(max_length=36, default="none")
    action_time = models.DateTimeField(auto_now_add=True)

    def vm_available(self):
        """ Current available VMs. """
        return self.vm_set.filter(status=VM.READY).count()

    def stacktrace_set(self, msg, stack_trace):
        """ Store the exception received while operating on a profile. """

        self.save()

        for exception in self.traceback_set.all():
            exception.delete()

        self.traceback_set.create(level=0, file_name=None, lineno=None,
                                  func_name=None, text=msg)
        level = 1
        for frame in traceback.extract_tb(stack_trace):
            fname, lineno, fn, text = frame
            self.traceback_set.create(level=level, file_name=fname,
                                      lineno=lineno, func_name=fn, text=text)
            level += 1

    def __contains__(self, srch):
        """ Return True if srch can be found in this object. """

        if srch in str(self.name):
            return True
        if self.hv.__contains__(srch):
            return True
        if srch in str(self.template_name):
            return True
        if srch in self.status_str():
            return True
        return False

    def status_str(self):
        """ Return status as a string. """

        if self.status == Profile.READY:
            return "ready"
        elif self.status == Profile.BAD:
            return "bad"
        else:
            raise ValueError("unknown value %d" % self.status)

    def deleteable(self):
        """ Return true if the model should be deleted.
        Profiles can only be deleted if all of the VMs have been
        deleted. Deleting a VM takes time. Only when maximum number
        is zero and all of the VMs have been actualy been deleted will
        the profile be deleted.
        """

        return self.vm_max == 0 and self.vm_set.count() == 0

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
