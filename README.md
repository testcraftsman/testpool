Manages a pool of VMs making sure they are available for quick use

This package is useful when users want to test against pristine VMs. VMs
are acquired, modified during testing then when finished are released back
to testpool. Where they are reclaimed, destroyed and cloned from a specified
template.

The goal is for VMs to always be available when tests need them and not 
waiting for VMs to be cloned.

To learn more http://testpool.readthedocs.io/en/latest/
