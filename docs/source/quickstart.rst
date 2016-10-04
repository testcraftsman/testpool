.. _QuickStartAnchor:

Quick Start
===============

Normally Testpool is installed on a central server and configured to
manager hypervisor content. Currently Testpool supports KVM which will be 
required for demonstration purposes. Testpool client content is installed
on satellite systems which interact with the Testpool server and hypvisors.

To expedite this guide, all Testpool content will be installed on a single
host. This can be either the KVM hypervisor or a seperate system. The
differences will be identified during the installation steps. Standalone mode 
is functionaly rich and useful for evaluation purposes.


KVM Installation 
----------------

For this quick start guide, we'll need a single VM named test.template running
on a KVM system. What the VM is running is not important and there are 
good instructions on the internet for setting up a KVM hypervisor and 
creating a VM. This section will provide references to these sites.

For installing KVM on Ubuntu 16.04, refer to this site https://help.ubuntu.com/community/KVM/Installation. Once complete, you will need the following 
information:

  - user and password that can install VMs. This is the user that is part of
    the libvirtd and kvm groups. 
  - IP Address of the KVM hypervisor if Testpool is not running on the
    hypervisor

For the rest of this quide, we'll assume the user is admin with password 
as password. Testpool will be installed on the hypervisor, so the IP address
used is localhost.

Now a single VM is required which represents the template that is managed
and cloned by Testpool. Using virt-manager, these instructions will create
an Ubuntu 16.04 server VM.

  #. sudo apt-get install virt-manager
  #. Run virt-manager
  #. From File, choose *Add Connection*.
  #. If applicable, choose *Connect to remote host*
  #. Enter admin for **Username** and IP address for the **Hostname**. This may
     be either localhost or the IP address of the KVM hypervisor.
     The default ssh method will probably work.
  #. Now connect and enter the user password.
  #. Select Hypervisor in the virt-manager,
  #. Choose **Create a new virtual manager**.
  #. Choose **Network Install (HTTP, FTP or NFS)** then Forward.
  #. For URL, enter **http://us.archive.ubuntu.com/ubuntu/dists/wily/main/installer-amd64/**


Testpool Installation
---------------------

We'll install Testpool from source, however prior the following must be
installed, starting with an Ubuntu 16.04 system:

  #. Install the latest virt-manager in order to install the latest python
     bindings::

       wget https://github.com/virt-manager/virt-manager/archive/v1.4.0.tar.gz
       tar -xf v1.4.0.tar.gz
       cd virt-manager-1.4.0
       sudo -H python ./setup.py install

  #. Install the latest python bindings to libvirt from::

       https://pypi.python.org/pypi/libvirt-python

  #. Install testpool from the github release area::

       wget https://github.com/testcraftsman/testpool/archive/0.0.3.tar.gz
       tar -xf 0.0.3.tar.gz

  #. Install several requried packages::

       cd testpool
       cat requirements.system | sudo xargs apt-get install
       sudo apt-file update
       sudo pip install -r requirements.pip
       sudo apt-get -f install

  #. Run Testpool database. In a shell run::

       cd testpool
       ./bin/tpl-db runserver -v 3

  #. In a second shell, run the Testpool daemon::

       cd testpool
       ./bin/tpl-daemon -v

A Short Tour
------------

In order for Testpool to manage VMs, Hypervisor information is registered
with the Testpool along with a single VM template.

Create a VM on the KVM hypervisor called test.template and keep it shutdown. Now create a testpool profile given the IP address and name of the VM template.

While running testpool on the hypervisor, use tpl CLI create a test pool 
profile::

  tpl profile add localhost kvm test.profile test.template 4

The Testpool Daemon will clone 4 VMs from the test.template. This can take
a while which is the point for this tool. Use **virt-manager** to see the 
VMs being created.
