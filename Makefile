# $Id: Makefile,v 1.6 2008/10/29 01:01:35 ghantoos Exp $
include defs.mk

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/testpool
PROJECT=testpool

check::


install:
	#sudo -H pip install --log pip.log --no-deps --upgrade dist/testpool-*.tar.gz
	python setup.py install --root $(DESTDIR) 

uninstall:
	sudo -H pip uninstall testpool

clean::
	python ./setup.py clean
	rm -rf dist build MANIFEST
	find . -name '*.pyc' -delete
	make -C debian $@
	rm -rf ../testpool_0.0.1* deb_dist


help::
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	python setup.py sdist

buildrpm:
	python setup.py bdist_rpm --post-install=rpm/postinstall \
                                  --pre-uninstall=rpm/preuninstall

.PHONY: deb.build
deb.build: MANIFEST.in ./setup.py 
	# build the source package in the parent directory
        # then rename it to project_version.orig.tar.gz
	#python setup.py sdist
	python setup.py --command-packages=stdeb.command bdist_deb
