# $Id: Makefile,v 1.6 2008/10/29 01:01:35 ghantoos Exp $
include defs.mk

DESTDIR=/
BUILDIR=$(CURDIR)/debian/myprojectname
PROJECT=testpool

check::

.PHONY:
build: MANIFEST.in ./setup.py 
	python ./setup.py -q build sdist bdist_wheel

install:
	sudo -H pip install --log pip.log --no-deps --upgrade dist/testpool-*.tar.gz
	python setup.py install --root $(DESTDIR) $(COMPILE)

uninstall:
	sudo -H pip uninstall testpool

clean::
	python ./setup.py clean
	rm -rf dist build MANIFEST
	find . -name '*.pyc' -delete


help::
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	python setup.py sdist $(COMPILE)

buildrpm:
	python setup.py bdist_rpm --post-install=rpm/postinstall \
               --pre-uninstall=rpm/preuninstall

builddeb:
	# build the source package in the parent directory
        # then rename it to project_version.orig.tar.gz
	python setup.py sdist $(COMPILE) --dist-dir=../
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot
