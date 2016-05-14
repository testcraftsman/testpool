ROOT=$(shell git rev-parse --show-toplevel)
include defs.mk
include $(ROOT)/defs.mk
test::
	./manage.py test -v 2

build::
	./manage.py collectstatic --noinput
