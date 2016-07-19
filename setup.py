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

#def _migrate(dir):
    #call([sys.executable, "manage.py", "migrate"], cwd=os.path.join(dir, packagename))

def _stop_service(dir):
    """ pre installation operations.

        Stop any running installation. 
    """
    from subprocess import call

    ##
    # Check to see if there is an existing database service running
    # and if so stop it.
    rtc = call(["service", "testpooldb", "status"])
    if rtc == 0:  # Service is running.
        rtc = call(["service", "testpooldb","stop"])
        if rtc == 0:
            logging.debug("failed to stop testpooldb")
    ##
        

##
# Run manage.py migrate
class post_install(install):
    """ Run content after main installation. """
    def run(self):

        logging.info("info log")
        logging.debug("debug log")
        logging.info("installation lib %s", self.install_lib)

        print "MARK: my own install", self.install_lib
        if os.path.exists(TESTPOOLDB_SERVICE):
            self.execute(_stop_service, (self.install_lib,),
                         msg="stopping testpool services")

        #self.execute(_migrate, (self.install_lib,),
        #             msg="Running post install task")
        install.run(self)
        print "MARK: my post install"


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
        ("/etc/init/", ["etc/init/testpooldb.conf"]),
    ],
    "classifiers": [
        'Development Status :: 1 - Pre-Alphe',
        'Programming Language :: Python :: 2.7',
    ],
    #"cmdclass": {'install': post_install},
}
setup(**setup_args)
