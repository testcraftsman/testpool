# $Id: Makefile,v 1.6 2008/10/29 01:01:35 ghantoos Exp $
include defs.mk

DESTDIR=/
BUILDIR=$(CURDIR)/debian/testpool
PROJECT=testpool
export VERSION:=`git describe --abbrev=0 --tag`

##
# Use find when __init__.py does not exist in the directory.
PYTHON_FILES+=testpool bin/*.py *.py
PYTHON_FILES+=`find ./examples -type f -name '*.py' -printf '%p '`
##


.PHONY: help
help::
	@echo "make deb.source - Create source package"
	@echo "make install - Install on local system"
	@echo "make rpm.build - Generate a rpm package"
	@echo "make deb.build - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"
	@echo "make check - unit test and pylint check"

pylint::
	$(PYLINT) $(PYTHON_FILES)

pycodestyle::
	pycodestyle --exclude=testpool/db/testpooldb/migrations \
            $(PYTHON_FILES)

info::
	@echo "version=${VERSION}"
	@echo "PYTHON_FILES=${PYTHON_FILES}"

clean::
	python ./setup.py clean
	rm -rf dist build MANIFEST .tox testpool/*.log
	rm -rf ../testpool_* testpool-* deb_dist testpool.egg-info
	find . -name '*.pyc' -delete

.PHONY: rpm.build
rpm.build:
	python setup.py bdist_rpm --post-install=rpm/postinstall \
                                  --pre-uninstall=rpm/preuninstall

.PHONY: deb.source
deb.source:
	python setup.py -q --command-packages=stdeb.command sdist_dsc

.PHONY: deb.build
deb.build: deb.source
	make -C testpool/db build
	cp debian/rules deb_dist/testpool-$(VERSION)/debian/rules
	cd deb_dist/testpool-$(VERSION);dpkg-buildpackage -uc -us

.PHONY: install
install:
	sudo -H dpkg --install deb_dist/python-testpool_$(VERSION)-1_all.deb

.PHONY: uninstall
uninstall:
	sudo -H dpkg --remove python-testpool

test::
	make -C testpool $@

setup:
	cat requirements.system | xargs apt-get -y install
	apt-file update
	pip install --upgrade pip
	pip install -qr requirements.dev
	pip install -qr requirements.txt
