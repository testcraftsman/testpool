# Copyright (c) 2015-2018 Mark Hamilton, All rights reserved
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
