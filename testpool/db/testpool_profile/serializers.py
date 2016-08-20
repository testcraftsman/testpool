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
Profile serializers for model data.
"""
from rest_framework import serializers
from testpooldb.models import Profile
from testpooldb.models import VM


# pylint: disable=R0903
class ProfileSerializer(serializers.ModelSerializer):
    """ Serialize ProfileModel. """

    class Meta(object):
        """ Define what is in a serialize response. """

        model = Profile
        fields = ('id', 'template_name', 'name', "vm_max", 'expiration',
                  'kvps')

# pylint: disable=R0903
class VMSerializer(serializers.ModelSerializer):
    """ Serialize ProfileModel. """

    class Meta(object):
        """ Define what is in a serialize response. """

        model = VM
        fields = ('id', 'name', "status", 'reserved')

#pylint: disable=C0103
#pylint: disable=W0223
class ProfileStatsSerializer(serializers.Serializer):
    """ Serialize ProfileStats object. """

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    vm_max = serializers.IntegerField()
    vm_free = serializers.IntegerField()
    vm_reserved = serializers.IntegerField()
    vm_released = serializers.IntegerField()
