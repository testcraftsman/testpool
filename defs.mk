ROOT=$(shell git rev-parse --show-toplevel)
SUBDEFS:=$(wildcard */defs.mk)
SUBMODULES:=$(foreach module,$(SUBDEFS),$(dir $(module)))
export PYTHONPATH:=$(ROOT):$(ROOT)/testpool/db
PYTHON=`which python`
PYTEST=pytest --cov=testpool -s --color=no -v 

PYTHON_FILES=

.PHONY: help
help::
	@echo "pylint - run pylint on python files."
	@echo "pycodestyle - run pep8 on python files."
	@echo "info - show makefile variables"

info::
	@echo "PYTHONPATH=$(PYTHONPATH)"

PYLINT=export PYTHONPATH=$(PYTHONPATH):$(ROOT)/testpool/db; \
       pylint --reports=n --disable=I0011 --disable=C1801 \
       --disable=R0801 --disable=E1101 --disable=I0012 --disable=R0914 \
       --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
       --generated-members=objects,MultipleObjectsReturned,get_or_create 

pylint:: $(addsuffix .pylint,$(PYTHON_FILES))


.PHONY: pylint
%.pylint::
	@$(PYLINT) $*

pylint:: $(addsuffix .pylint,$(PYTHON_FILES))

.PHONY: python27
python27::
	@python -m compileall $* $(PYTHON_FILES)

.PHONY: test
test:: 

.PHONY: debug_mark
debug_mark:: 
	grep --exclude=*~ --exclude=*.pickle --exclude=*.pyc -Hrn MARK */ && exit 1 || exit 0

pycodestyle::

check:: pycodestyle pylint python27 test debug_mark
clean::
	find . -name "#*" -delete
	find . -name ".#*" -delete
	find . -name "*~" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
