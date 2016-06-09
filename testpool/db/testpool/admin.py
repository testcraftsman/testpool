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
 Admin interface to test models.
"""
from django.contrib import admin

# Register your models here.
from . import models


class KeyAdmin(admin.ModelAdmin):
    """ View key. """

    model = models.Key
    list_display = ("value", "config_type", )


class KVPAdmin(admin.ModelAdmin):
    """ View Test Key. """

    model = models.KVP
    list_display = ("key", "value", )


class VMAdmin(admin.ModelAdmin):
    """ Show set of keys that associate a testsuite. """

    model = models.VM


class ProfileKVPAdmin(admin.ModelAdmin):
    """ Show set of keys that associate a testsuite. """

    model = models.ProfileKVP


class ProfileAdmin(admin.ModelAdmin):
    """ Show set of keys that associate a testsuite. """

    model = models.Profile

    inlines = [ProfileKVPAdmin]


class HVAdmin(admin.ModelAdmin):
    """ Administrate testplan content. """

    model = models.HV


admin.site.register(models.Key, KeyAdmin)
admin.site.register(models.KVP, KVPAdmin)
admin.site.register(models.VM, VMAdmin)
admin.site.register(models.ProfileKVP, ProfileKVPAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.HV, HVAdmin)
