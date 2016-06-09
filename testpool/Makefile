ROOT=$(shell git rev-parse --show-toplevel)
include defs.mk
include $(ROOT)/defs.mk

test::
	py.test -v core/*.py
