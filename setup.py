import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from testpool import __version__, __author__

from distutils.dist import Distribution
def custom_has_scripts(self):
    return True
Distribution.has_scripts = custom_has_scripts

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

fpath = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(fpath) as hdl:
    REQUIREMENTS = hdl.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def _migrate(dir):
    from subprocess import call
    print "MARK: install_lib", dir
    #os.system("echo mark > /tmp/log")
    #call([sys.executable, "manage.py", "migrate"], cwd=os.path.join(dir, packagename))

##
# Run manage.py migrate
class post_install(install):
    def run(self):
        print "MARK: my own install"
        #self.execute(_migrate, (self.install_lib,),
        #             msg="Running post install task")
        install.run(self)
        print "MARK: my post install"
	os.system("echo mark >> /tmp/log")

setup_args = {
    "name": 'testpool',
    "version":__version__,
    "packages": ['testpool'],
    "scripts": ["bin/tpl", "bin/testpooldaemon", "bin/testpooldb"],
    "license": 'GPLv3',
    "description": 'Manage and recycle pools of VMs.',
    "long_description": README,
    "url": 'https://github.com/testbed/testpool.git',
    "author": __author__,
    "author_email": 'mark.lee.hamilton@gmail.com',
    "install_requires": REQUIREMENTS.split("\n"),
    "data_files": [
        ("/etc/testpool/", ["etc/testpool/testpool.conf"]),
        ("/etc/init/", ["etc/init/testpooldb.conf"]),
    ],
    "classifiers": [
        'Development Status :: 1 - Pre-Alphe',
        'Programming Language :: Python :: 2.7',
    ],
    "cmdclass": {'install': post_install},
}
setup(**setup_args)
