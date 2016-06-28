ROOT=$(shell git rev-parse --show-toplevel)
include defs.mk
include $(ROOT)/defs.mk

test::
	export PYTHONPATH=$(PYTHONPATH);py.test -v core
