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
Pool serializers for model data.
"""
from rest_framework import serializers
from testpooldb.models import Pool
from testpooldb.models import Resource
from testpooldb.models import Key


# pylint: disable=R0903
class PoolSerializer(serializers.ModelSerializer):
    """ Serialize PoolModel. """

    class Meta(object):
        """ Define what is in a serialize response. """

        model = Pool
        fields = ('id', 'template_name', 'name', "resource_max", 'expiration',
                  'kvps', "resource_available")


class KeySerializer(serializers.ModelSerializer):
    """ Serialize PoolModel. """

    class Meta(object):
        """ Define what is in a serialize response. """

        model = Key
        fields = ('value',)


class KVPListSerializer(serializers.ModelSerializer):
    """ Serialize KVP List. """

    def to_representation(self, instance):
        return instance.key.value, instance.value


# pylint: disable=R0903
class ResourceSerializer(serializers.ModelSerializer):
    """ Serialize Resource. """

    kvps = KVPListSerializer(many=True, read_only=True)

    class Meta(object):
        """ Define what is in a serialize response. """

        model = Resource
        fields = ('id', 'name', "status", 'ip_addr', 'action_time', 'kvps')


# pylint: disable=C0103
# pylint: disable=W0223
class PoolStatsSerializer(serializers.Serializer):
    """ Serialize PoolStats object. """

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    resource_max = serializers.IntegerField()
    rsrc_ready = serializers.IntegerField()
    rsrc_reserved = serializers.IntegerField()
    rsrc_pending = serializers.IntegerField()
