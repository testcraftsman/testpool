ROOT=$(shell git rev-parse --show-toplevel)
include defs.mk
include $(ROOT)/defs.mk

test::
	export PYTHONPATH=$(PYTHONPATH);${PYTEST} core libexec/fake libexec/docker
