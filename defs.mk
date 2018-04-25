ROOT=$(shell git rev-parse --show-toplevel)
SUBDEFS:=$(wildcard */defs.mk)
SUBMODULES:=$(foreach module,$(SUBDEFS),$(dir $(module)))
export PYTHONPATH:=$(ROOT):$(ROOT)/testpool/db
PYTHON=`which python`

PYTHON_FILES=

.PHONY: help
help::
	@echo "pylint - run pylint on python files."
	@echo "pycodestyle - run pep8 on python files."
	@echo "info - show makefile variables"

info::
	@echo "PYTHONPATH=$(PYTHONPATH)"


.PHONY: subdirs $(SUBMODULES)
$(SUBMODULES):
	make -C $@ $(MAKECMDGOALS)

subdirs: $(SUBMODULES)

PYLINT=export PYTHONPATH=$(PYTHONPATH):$(ROOT)/testpool/db; \
       pylint --reports=n --disable=I0011 --disable=C1801 \
       --disable=R0801 --disable=E1101 --disable=I0012 --disable=R0914 \
       --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
       --generated-members=objects,MultipleObjectsReturned,get_or_create 

pylint:: $(addsuffix .pylint,$(PYTHON_FILES)) subdirs


.PHONY: pylint
%.pylint::
	@$(PYLINT) $*

pylint:: $(addsuffix .pylint,$(PYTHON_FILES)) subdirs

%.python27:
	python -m compileall $*

.PHONY: python27
python27:: $(addsuffix .python27,$(PYTHON_FILES))

.PHONY: test
test:: subdirs

.PHONY: debug_mark
debug_mark:: 
	grep --exclude=*~ --exclude=*.pickle --exclude=*.pyc -Hrn MARK */ && exit 1 || exit 0

pycodestyle::

check:: pycodestyle pylint subdirs python27 test debug_mark
clean::
	find . -name "#*" -delete
	find . -name ".#*" -delete
	find . -name "*~" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
