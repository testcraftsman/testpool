# testpool
Manages a pool of VMs making sure they are available for quick use

This package is useful when users want to test against pristine VMs. VMs
are acquired, modified during testing. When finished, the VM released
where it is destroyed and new VM is cloned in its place.

The goal is for VMs to always be available when tests need them and not 
waiting for VMs to be cloned.


Installation

   sudo pip install libvirt-python django-split-settings>=0.1.3 testpool

KVM Support

Complete steps for install KVM content can be found on the internet. 
Additionaly, this package requires python binding to libvirt. The following
explains how to install the necessary packages but please consult official
documentation on how to setup and configure KVM.

   sudo apt install qemu-kvm libvirt-bin libvirt-dev

Debian Packaging

Before debian packages can be created apt-file must be installed and updated
so that the python requirements.txt file can be mapped to equivalent 
debian package dependencies.

  sudo apt-get install apt-file
  sudo apt-file update

Make sure to set EMAIL before using dch
export EMAIL="Mark Hamilton <mark.lee.hamilton@gmail.com>"

Also note that versions are incremented in the change log
  dch -U
