#!/bin/sh
export PYTHONPATH=/home/mark/ws/testpool
#python ./testpool/libexec/kvm/testsuite.py
#cd testpool/db;make test
cd testpool/libexec/memory;python ./testsuite.py
