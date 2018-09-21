include defs.mk
include ../../defs.mk
test::
	./manage.py test -v 2

build::
	./manage.py collectstatic --noinput

clean::
	rm -rf ./static
