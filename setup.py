##
# \todo figure out how to post content to the log
import logging
import os
import pkgutil
import subprocess
from subprocess import call
from setuptools import setup, find_packages
from setuptools.command.install import install
import testpool.version

AUTHOR = "Mark Hamilton"
AUTHOR_EMAIL = "mark.lee.hamilton@gmail.com"

##
# Figure out version based on debian changelog
version = testpool.version.package_version
##

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

fpath = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(fpath) as hdl:
    REQUIREMENTS = hdl.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup_args = {
    "name": 'testpool',
    "version": version,
    "packages": find_packages(),
    "include_package_data": True,
    "scripts": ["bin/tpl", "bin/tpl-daemon", "bin/tpl-db"],
    "license": 'GPLv3',
    "description": 'Manage and recycle pools of VMs.',
    "long_description": README,
    "url": 'https://github.com/testbed/testpool.git',
    "maintainer": AUTHOR,
    "maintainer_email": AUTHOR_EMAIL,
    "author": AUTHOR,
    "author_email": AUTHOR_EMAIL,
    "install_requires": REQUIREMENTS,
    "data_files": [
        ("testpool/etc", ["etc/testpool/testpool.yml",
                          "etc/logrotate.d/testpool"]),
        ("testpool/systemd/", ["scripts/systemd/tpl-db.service"]),
        ("testpool/systemd/", ["scripts/systemd/tpl-daemon.service"]),
    ],
    "classifiers": [
        'Development Status :: 1 - Pre-Alpha',
        'Programming Language :: Python :: 2.7',
    ],
}
setup(**setup_args)
