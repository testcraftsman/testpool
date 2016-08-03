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


# pylint: disable=R0903
class ProfileSerializer(serializers.ModelSerializer):
    """ Serialize profile object. """
    class Meta(object):
        """ Define what is in a serialize response. """
        model = Profile
        fields = ('id', 'name', "vm_max")
