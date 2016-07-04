import os
from setuptools import setup

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

setup(
    name='testpool',
    version=__version__,
    packages=['testpool'],
    scripts=["bin/tpl", "bin/testpooldaemon"],
    include_package_data=True,
    license='GPLv3',
    description='Comprehensive web-based test tracking software.',
    long_description=README,
    url='https://github.com/testbed/testpool.git',
    author=__author__,
    author_email='mark.lee.hamilton@gmail.com',
    install_requires=REQUIREMENTS.split("\n"),
    data_files=[
        ("testpool/etc", []),
        ("testpool/etc", ["/etc/mysql.cnf"]),
    ] + STATIC_FILES,
    classifiers=[
        'Development Status :: 1 - Pre-Alphe',
        'Environment :: Web Environment',
        'Framework :: Testbed',
        'Intended Audience :: Developers',
        'Intended Audience :: Managers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
)
