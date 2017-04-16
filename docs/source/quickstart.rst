.. _QuickStartAnchor:

Quick Start
===============

Testpool maintains a pool of pristine VMs cloned from a template. Users 
can immediate acquire a VM, use it and then throw it away. Testpool
then replaces discarded VMs with a fresh clone.  Cloning VMs can take a
considerable amount of time, but with a pool of VMs, acquiring a single VM
is immediate.

Normally Testpool is installed on a central server and configured to
manage several hypervisors. Testpool supports KVM which is required for 
this demonstration. 

To expedite this guide, Testpool content is installed on the KVM hypervisor.
For final installation, Testpool can be installed either the hypervisor or a
separate system. The differences will be identified during the installation
steps.


KVM Installation 
----------------

For this quick start guide, we'll need a single VM named test.template on 
the hypervisor which is off and ready to be cloned.  When the VMs starts
it must use DHCP to acquire its IP address. What the VM is running is
not important and there are good instructions on the internet for setting up a
KVM hypervisor and creating a VM.  For installing KVM on Ubuntu 16.04, refer
to this site https://help.ubuntu.com/community/KVM/Installation. Once complete, you will need the following information:

  - user and password that can install VMs. This is the user that is part of
    the libvirtd and kvm groups. 
  - IP Address of the KVM hypervisor if Testpool is not running on the
    hypervisor

For the rest of this guide, we'll assume the user tadmin with password 
'password'. Since Testpool is installed on the hypervisor, the IP address used is
localhost.

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
  #. For URL, enter **http://us.archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64/** The URL changes periodically, check the Ubuntu site for the 
     latest valid links.


Testpool Installation
---------------------

We'll install Testpool from source.

  #. Download Testpool from github release area::

       wget https://github.com/testcraftsman/testpool/archive/v0.0.7.tar.gz
       tar -xf testpool-0.0.7.tar.gz

  #. Install several required packages::

       cd testpool
       cat requirements.system | sudo xargs apt-get install
       sudo apt-file update
       sudo pip install -qr requirements.txt
       sudo pip install easydict
       sudo pip install django-pure-pagination==0.2.1
       sudo pip install django-split-settings==0.1.3

  #. Run Testpool database. In a shell run::

       ./bin/tpl-db runserver -v 3

  #. In a second shell, run the Testpool daemon::

       ./bin/tpl-daemon -v

A Short Tour
------------

In order for Testpool to manage VMs, Hypervisor information is registered
with Testpool along with a VM template.

Create a VM on the KVM hypervisor called test.template and keep it shutdown. Now create a Testpool profile given the IP address and name of the VM template.
Since we're running on the hypervisor, the IP address is localhost.

Where hypervisor-ip is replaced with the actual Hypervisor IP address.  While 
running Testpool on the hypervisor, use the tpl CLI to create a test pool 
profile::

  ./bin/tpl profile add example kvm qemu:///system test.template 3

Confirm the profile is valid::

  ./bin/tpl profile detail example

The Testpool Daemon will clone 3 VMs from the test.template. This can take
a while which is the point of this product. In that, Testpool generates
new clean clones based on test.template. The VMs available line in the detail
output shows the current number of available VMs. Use **virt-manager** to see
the VMs being created. 

From this point, Testpool daemon is cloning VMs. There are several examples
to look through. The file examples/rest.py provides documentation and 
demonstrates how to use Testpool's REST interface. Simply refer to the 
file examples/rest.py.

Additionally, Testpool-client can be installed which provides a python
API on top of the REST interface. To learn more, http://testpool-client.readthedocs.io/en/latest.

.. literalinclude:: /../../examples/rest.py
