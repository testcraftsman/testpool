# (c) 2016 Mark Hamilton, <mark.lee.hamilton@gmail.com>
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
View pool information.
"""
import json
import logging
from django.shortcuts import render_to_response
from testpooldb import models

LOGGER = logging.getLogger("django.testpool")


# pylint: disable=R0902
# pylint: disable=R0903
class PoolStats(object):
    """ Provides individual pool stats used in the pool view. """

    def __init__(self, pool):
        """Contruct a pool view. """

        ##
        # pylint: disable=C0103
        # The ID is needed for the JSON view.
        self.id = pool.id
        #
        self.connection = pool.host.connection
        self.name = pool.name
        self.resource_max = pool.resource_max
        self.rsrc_ready = 0
        self.rsrc_reserved = 0
        self.rsrc_pending = 0
        self.rsrc_bad = 0

        for item in models.Resource.objects.filter(pool=pool):
            if item.status == models.Resource.RESERVED:
                self.rsrc_reserved += 1
            elif item.status == models.Resource.PENDING:
                self.rsrc_pending += 1
            elif item.status == models.Resource.READY:
                self.rsrc_ready += 1
            elif item.status == models.Resource.BAD:
                self.rsrc_bad += 1


def pool_list(_):
    """ Summarize product information. """
    LOGGER.debug("pool")

    pools = models.Pool.objects.all()
    pools = [PoolStats(item) for item in pools]

    html_data = {"pools": pools}
    return render_to_response("pool/list.html", html_data)


def detail(_, pool):
    """ Provide pool details. """

    LOGGER.debug("pool/detail/%s", pool)

    pool1 = models.Pool.objects.get(name=pool)
    rsrcs = [item for item in models.Host.objects.filter(pool=pool1)]
    html_data = {
        "rsrcs": rsrcs,
        "pool": pool1
    }

    return render_to_response("pool/detail.html", html_data)


def dashboard(_):
    """ Provide summary of all pools. """

    LOGGER.debug("views.dashboard")

    return render_to_response('pool/index.html')
