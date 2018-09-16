include defs.mk
include ../../defs.mk
test::
	./manage.py test -v 2

build::
        rm -rf ./static
	./manage.py collectstatic --noinput
	cp -r /usr/local/testpool/static ./static
