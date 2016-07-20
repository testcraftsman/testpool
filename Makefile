# $Id: Makefile,v 1.6 2008/10/29 01:01:35 ghantoos Exp $
include defs.mk

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/testpool
PROJECT=testpool
export VERSION:=`python -c "import testpool; print testpool.__version__"`

info::
	@echo "version ${VERSION}"



uninstall:
	sudo -H pip uninstall testpool

clean::
	python ./setup.py clean
	rm -rf dist build MANIFEST
	find . -name '*.pyc' -delete
	rm -rf ../testpool_* testpool-* deb_dist


help::
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	python setup.py --command-packages=stdeb.command sdist_dsc

.PHONY: rpm.build
rpm.buil:
	python setup.py bdist_rpm --post-install=rpm/postinstall \
                                  --pre-uninstall=rpm/preuninstall

.PHONY: deb.build
deb.build: MANIFEST.in ./setup.py 
	python setup.py --command-packages=stdeb.command bdist_deb

install:
	sudo dpkg --install deb_dist/python-testpool_$(VERSION)-1_all.deb
