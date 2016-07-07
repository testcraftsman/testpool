#!/bin/sh
export PYTHONPATH=/home/mark/ws/testpool
py.test testpool/libexec/fake/testsuite.py
#py.test testpool/libexec/fake/testsuite.py -k test_pop
