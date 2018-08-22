# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
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


class ResourceAdmin(admin.ModelAdmin):
    """ Show set of keys that associate a testsuite. """

    model = models.Resource


class PoolAdmin(admin.ModelAdmin):
    """ Show set of keys that associate a testsuite. """

    model = models.Pool


class HostAdmin(admin.ModelAdmin):
    """ Administrate testplan content. """

    model = models.Host


admin.site.register(models.Key, KeyAdmin)
admin.site.register(models.KVP, KVPAdmin)
admin.site.register(models.Resource, ResourceAdmin)
admin.site.register(models.Pool, PoolAdmin)
admin.site.register(models.Host, HostAdmin)
