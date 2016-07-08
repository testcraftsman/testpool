include defs.mk

check::

.PHONY:
build: MANIFEST.in ./setup.py 
	python ./setup.py -q build sdist bdist_wheel

install:
	sudo -H pip install --log dist/pip.log --upgrade dist/testpool-*.tar.gz

uninstall:
	sudo -H pip uninstall testpool

clean::
	python ./setup.py clean
	rm -rf dist build testpool.egg-info
