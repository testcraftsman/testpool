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
Provides general settings for testpool.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
##
# Location of the test database root directory.
TEST_DBSITE_DIR = os.path.abspath(os.path.join(BASE_DIR, "db"))

PLUGINS = {
    'testpool.libexec',
}


##
# log formatting
FMT = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'


CFG_FILE = "/etc/testpool/testpool.yml"
