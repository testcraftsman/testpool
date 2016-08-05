# testpool
Provide a pool of pre populated VMs for quick access 

KVM Support

Complete steps for install KVM content can be found on the internet. 
Additionaly, this package requires python binding to libvirt. The following
explains how to install the necessary packages but please consult official
documentation on how to setup and configure KVM.

   sudo apt install qemu-kvm libvirt-bin libvirt-dev
   sudo pip install libvirt-python


Debian Packaging

Make sure to set EMAIL before using dch
export EMAIL="Mark Hamilton <mark.lee.hamilton@gmail.com>"


Also note that versions are incremented in the change log
  dch -U
