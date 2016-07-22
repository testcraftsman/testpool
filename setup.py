##
# \todo figure out how to post content to the log
import logging
import os
import pkgutil
from subprocess import call
from setuptools import setup, find_packages
from setuptools.command.install import install

from testpool import __version__, __author__


TESTPOOLDB_SERVICE = "/etc/init/testpooldb.conf"

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

fpath = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(fpath) as hdl:
    REQUIREMENTS = hdl.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

##
# Run manage.py migrate
class install_service(install):
    """ Run content after main installation. """
    def run(self):
        install.run(self)

        logging.info("info log")
        logging.debug("debug log")
        logging.info("installation lib %s", self.install_lib)

        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        create_service_script_path = os.path.join(current_dir_path, 'testpool', 'install_scripts', 'create_service.sh')
        #subprocess.check_output([create_service_script_path])

setup_args = {
    "name": 'testpool',
    "version":__version__,
    "packages": find_packages(),
    "include_package_data": True,
    "scripts": ["bin/tpl", "bin/testpooldaemon", "bin/testpooldb"],
    "license": 'GPLv3',
    "description": 'Manage and recycle pools of VMs.',
    "long_description": README,
    "url": 'https://github.com/testbed/testpool.git',
    "author": __author__,
    "author_email": 'mark.lee.hamilton@gmail.com',
    #"install_requires": REQUIREMENTS.split("\n"),
    "data_files": [
        ("testpool/etc", ["etc/testpool/testpool.conf"]),
        ("testpool/systemd/", ["scripts/systemd/testpooldb.service"]),
    ],
    "classifiers": [
        'Development Status :: 1 - Pre-Alphe',
        'Programming Language :: Python :: 2.7',
    ],
    #"cmdclass": {'install': install_service},
}
setup(**setup_args)
