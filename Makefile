include defs.mk

test::
	make -C testpool test

check::

.PHONY:
build: MANIFEST.in ./setup.py 
	python ./setup.py build sdist bdist_wheel

install: build
	sudo pip install --upgrade dist/*.tar.gz

uninstall:
	sudo pip uninstall testpool

test::
	py.test -v testpool
