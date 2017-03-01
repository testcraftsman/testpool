.. _QuickStartAnchor:

Quick Start
===============

Testpool clones VMs from a template VM. Testpool monitors each VM waiting for their management
interface to be assgiend an IP address, usually through DHCP. Once assigned,
Testpool makes the VM available for users. Users acquire a VM and then release
it when done. Where Testpool replaces the VM with a fresh clone. Cloning 
VMs can take a considerable amount of time. Testpool manages the VMs so
that acquiring VMs is immediate.

Normally Testpool is installed on a central server and configured to
manager several hypervisors. Testpool supports KVM which is required for 
this demonstration. 

To expedite this guide, Testpool content will be installed on the KVM 
hypervisor. For final installation, Testpool can be installed either the 
hypervisor or a separate system. The differences will be identified during 
the installation steps.


KVM Installation 
----------------

For this quick start guide, we'll need a single VM named test.template on 
the hypervisor which is off and ready to be cloned.  What the VM is running is
not important and there are good instructions on the internet for setting up a
KVM hypervisor and creating a VM. This section will provide references to
these sites.

For installing KVM on Ubuntu 16.04, refer to this site https://help.ubuntu.com/community/KVM/Installation. Once complete, you will need the following 
information:

  - user and password that can install VMs. This is the user that is part of
    the libvirtd and kvm groups. 
  - IP Address of the KVM hypervisor if Testpool is not running on the
    hypervisor

For the rest of this guide, we'll assume the user tadmin with password 
as 'password'. Since testpool will be installed on the hypervisor, so the IP
 address used is localhost.

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
  #. For URL, enter **http://us.archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64/** The URL changes periodically, check the ubuntu site for the 
     latest valid links.


Testpool Installation
---------------------

We'll install Testpool from source.

  #. Download testpool from github release area::

       wget https://github.com/testcraftsman/testpool/archive/v0.0.7.tar.gz
       tar -xf testpool-0.0.7.tar.gz

  #. Install several required packages::

       cd testpool
       cat requirements.system | sudo xargs apt-get install
       sudo apt-file update
       sudo pip install -qr requirements.pip
       sudo apt-get -f install

  #. Setup Testpool database, in  a shell run::

       cd testpool/testpool/db
       ./manage.py migrate 


  #. Run Testpool database. In a shell run::

       cd testpool
       ./bin/tpl-db runserver -v 3

  #. In a second shell, run the Testpool daemon::

       cd testpool
       ./bin/tpl-daemon -v

A Short Tour
------------

In order for Testpool to manage VMs, Hypervisor information is registered
with the Testpool along with a name of a single VM template.

Create a VM on the KVM hypervisor called test.template and keep it shutdown. Now create a testpool profile given the IP address and name of the VM template.
Since we're running on the hypervisor, the IP address is localhost.

Where hypervisor-ip is replaced with the actual Hypervisor IP address.  While 
running testpool on the hypervisor, use the tpl CLI to create a test pool 
profile::

  ./bin/tpl profile add example kvm qemu:///system test.template 3

Confirm the profile is valid::

  ./bin/tpl profile detail example

The Testpool Daemon will clone 3 VMs from the test.template. This can take
a while which is the point of this tool. In that Testpool, maintains a 
pool of VMs which are immediatelly available.  Use **virt-manager** to see the 
VMs being created. 

From this point, Testpool is cloning VMs for use, the examples folder relies on
this configuration to run. Refer to the example below to see how to use Testpool.

.. literalinclude:: /../../examples/python_api.py
