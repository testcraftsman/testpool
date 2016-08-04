##
# \todo figure out how to post content to the log
import logging
import os
import pkgutil
from subprocess import call
from setuptools import setup, find_packages
from setuptools.command.install import install

from testpool import __version__, __author__, __email__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

fpath = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(fpath) as hdl:
    REQUIREMENTS = hdl.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup_args = {
    "name": 'testpool',
    "version":__version__,
    "packages": find_packages(),
    "include_package_data": True,
    "scripts": ["bin/tpl", "bin/tpl-daemon", "bin/tpl-db"],
    "license": 'GPLv3',
    "description": 'Manage and recycle pools of VMs.',
    "long_description": README,
    "url": 'https://github.com/testbed/testpool.git',
    "author": __author__,
    "author_email": __email__,
    #"install_requires": REQUIREMENTS.split("\n"),
    "data_files": [
        ("testpool/etc", ["etc/testpool/testpool.conf"]),
        ("testpool/systemd/", ["scripts/systemd/tpl-db.service"]),
    ],
    "classifiers": [
        'Development Status :: 1 - Pre-Alphe',
        'Programming Language :: Python :: 2.7',
    ],
}
setup(**setup_args)
