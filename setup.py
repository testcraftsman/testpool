from distutils.core import setup
from distutils.command.install import install
import os

from testpool import __version__, __author__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

fpath = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(fpath) as hdl:
    REQUIREMENTS = hdl.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def walkdir(dirname):
    """ Retrieve a list of files.

    Since this is part of setup.py, files are pruned after passed to
    data_files based on MANIFEST.IN. """
    for cur, ddirs, ffiles in os.walk(dirname):
        for ffile in ffiles:
            fext = os.path.splitext(ffile)[1]
            yield os.path.join(cur, ffile)

        for ddir in ddirs:
            walkdir(os.path.join(cur, ddir))

##
# strip http
STATIC_FILES = [(os.path.split("testpool" + item[4:])[0], [item])
                 for item in walkdir("http/static")]

def _migrate(dir):
    from subprocess import call
    print "MARK: install_lib", dir
    os.system("echo mark > /tmp/log")
    call([sys.executable, "manage.py", "migrate"], cwd=os.path.join(dir, packagename))

##
# Run manage.py migrate
class PostInstallCommand(install):
    def run(self):
	install.run(self)
	self.execute(_migrate, (self.install_lib,),
                     msg="Running post install task")


setup(
    name='testpool',
    version=__version__,
    packages=['testpool'],
    scripts=["bin/tpl", "bin/testpooldaemon", "bin/testpooldb"],
    include_package_data=True,
    license='GPLv3',
    description='Manage and recycle pools of VMs.',
    long_description=README,
    url='https://github.com/testbed/testpool.git',
    author=__author__,
    author_email='mark.lee.hamilton@gmail.com',
    install_requires=REQUIREMENTS.split("\n"),
    data_files=[
        ("/etc/testpool/", ["etc/testpool/testpool.conf"]),
        ("/etc/init/", ["etc/init/testpooldb.conf"]),
    ],
    classifiers=[
        'Development Status :: 1 - Pre-Alphe',
        'Programming Language :: Python :: 2.7',
    ],
    cmdclasss={
        'install': PostInstallCommand,
    },
)
