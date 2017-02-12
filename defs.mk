SUBDEFS:=$(wildcard */defs.mk)
SUBMODULES:=$(foreach module,$(SUBDEFS),$(dir $(module)))
ROOT=$(shell git rev-parse --show-toplevel)
PYTHONPATH:=$(ROOT):$(ROOT)/testpool/db

.PHONY: help
help::
	echo "pylint - run pylint on python files."
	echo "pep8 - run pep8 on python files."

.PHONY: subdirs $(SUBMODULES)
$(SUBMODULES):
	make -C $@ $(MAKECMDGOALS)

subdirs: $(SUBMODULES)


.PHONY: pylint
%.pylint::
	@export PYTHONPATH=$(PYTHONPATH);pylint --reports=n --disable=I0011 \
          --disable=R0801 --disable=E1101 --disable=I0012 --disable=R0914 \
          --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
	  --generated-members=objects,MultipleObjectsReturned,get_or_create $*

pylint:: $(addsuffix .pylint,$(PYTHON_FILES)) subdirs


%.pep8:
	pep8 $*

.PHONY: pep8
pep8:: $(addsuffix .pep8,$(PYTHON_FILES)) subdirs


%.python27:
	python -m compileall $*

.PHONY: python27
python27:: $(addsuffix .python27,$(PYTHON_FILES))

.PHONY: test
test:: subdirs

.PHONY: debug_mark
debug_mark:: 
	grep --exclude=*~ --exclude=*.pickle --exclude=*.pyc -Hrn MARK */ && exit 1 || exit 0

check:: pep8 pylint subdirs python27 test debug_mark
clean::
	find . -name "#*" -delete
	find . -name ".#*" -delete
	find . -name "*~" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
