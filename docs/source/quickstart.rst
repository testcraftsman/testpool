.. _QuickStartAnchor:

Quick Start
===============

Testpool maintains a pool of pristine VMs cloned from a template. Users 
can immediate acquire a VM, use it and then throw it away. Testpool
then replaces discarded VMs with a fresh clone.  Cloning VMs can take a
considerable amount of time, but with a pool of VMs, acquiring a single VM
is immediate. Testpool supports KVM and docker.

There are three demonstrations of Testpool. One uses fake resources to
demostrate a large deployment. The second demo usss docker and is designed
to work on a sinlge laptop for the sake of having an easy demo. The third
uses KVM hypervisors.

Simulation Demonstration 
------------------------

Testpool Installation
------------

We'll install Testpool from Debian.

  #. Install several required packages::

       sudo apt-get install -y apt-file libvirt0 virtinst pm-utils
       sudo apt-get install -y libvirt-bin libvirt-dev qemu-system debhelper
       sudo apt-get install -y python-yaml python-pip python-all enchant
       sudo apt-get install -y fakeroot dh-python
       sudo apt-file update
       sudo pip install -q docker==3.4.1 docker-pycreds==0.3.0 requests>=2.19.1
       sudo pip install -q pytz>=2018.5 Django==1.11.13
       sudo pip install -q djangorestframework>=3.8.2
       sudo pip install -q django-pure-pagination==0.3.0
       sudo pip install -q django-split-settings==0.3.0
       sudo pip install -q libvirt-python==4.0 ipaddr>=2.1.11 structlog>=16.1.0
       sudo pip install -q pyyaml easydict pyenchant==2.0.0 pybuild==0.2.6

  #. Download Testpool from github release page:
   
    Check for the latest release at:

    https://github.com/testcraftsman/testpool/releases

    below is an example:

    https://github.com/testcraftsman/testpool/releases/download/v0.1.5/python-testpool_0.1.5-1_all.deb
    sudo dpkg -i python-testpool_0.1.5-1_all.deb

  #. Check testpool services are running:

       systemctl status tpl-daemon
       systemctl status tpl-db

  #. Run the Testpool demo that ships with the product

       tpl-demo -v 

     The demo creates several fake pools, then periodically 
     acquires a resource then releases it. After 60 seconds, all 
     resources are released for 1 minute. The dashboard shows the
     status of the various resources:
   
       http://127.0.0.1:8000/testpool/view/dashboard

     Alternatively, *tpl-demo* can be run with *--product docker*. Don't run
     tpl-demo if going through the next section in the **Short Tour**.


A Short Tour
------------

In order for Testpool to manage VMs, Hypervisor information is registered
with Testpool along with a VM template.


KVM Hypervisor Demonstration
----------------------------

Normally Testpool is installed on a central server and configured to
manage several hypervisors. Testpool supports KVM which is required for 
this demonstration. 

To expedite this guide, Testpool content is installed on the KVM hypervisor.
For final installation, Testpool can be installed either on the hypervisor or a
separate system. The differences will be identified during the installation
steps.


Testpool Stack
--------------

Testpool consists of several releated products. They are:

  - Testpool-client - installed on each client, this package provides an API
   to acquire and release VMs.  This is useful when writing tests and not 
   wanting to use the REST interface directly.

  - Testpool-beat - pushes testpool metrics to logstash. This is useful for 
    monitoring VM pools.

Make sure to install the appropriate major and minor version that matches the testpool package. For example, if the version of Testpool is 0.1.0. Then install 0.1.Y of Testpool-client and Testpool-beat. Where Y can be any value.


KVM Installation 
----------------

For this quick start guide, we'll need a single VM named test.template on 
the hypervisor which is off and ready to be cloned.  When the VMs starts
it must use DHCP to acquire its IP address. What the VM is running is
not important and there are good instructions on the internet for setting up a
KVM hypervisor and creating a VM.  For installing KVM on Ubuntu 18.04, refer
to this site https://help.ubuntu.com/community/KVM/Installation. Once complete, you will need the following information:

  - user and password that can install VMs. This is the user that is part of
    the libvirtd and kvm groups. 
  - IP Address of the KVM hypervisor if Testpool is not running on the
    hypervisor

For the rest of this guide, we'll assume the user tadmin with password 
'password'. Since Testpool is installed on the hypervisor, the IP address used
is localhost.

Now a single VM is required which represents the template that is managed
and cloned by Testpool. Using virt-manager, these instructions will create
an Ubuntu 16.04 server VM.

  #. sudo apt-get install virt-manager
  #. Run **virt-manager**
  #. From File, choose **Add Connection**.
  #. If applicable, choose **Connect to remote host**
  #. Enter admin for **Username** and IP address for the **Hostname**. This may
     be either localhost or the IP address of the KVM hypervisor.
     The default ssh method will probably work.
  #. Now connect and enter the user password.
  #. Select Hypervisor in the virt-manager,
  #. Choose **Create a new virtual manager**.
  #. Choose **Network Install (HTTP, FTP or NFS)** then Forward.
  #. For URL, enter **http://us.archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/** The URL changes periodically, check the Ubuntu site for the 
     latest valid links.
  #. Choose appropriate RAM and CPU. For a demo, select 512 and 1 CPU.
  #. Create a disk with 5 GiB of space.
  #. Then select Finish fro the network setup.

A Short Tour
------------

In order for Testpool to manage VMs, Hypervisor information is registered
with Testpool along with a VM template.

Create a VM on the KVM hypervisor called test.template and keep it shutdown. Now create a Testpool pool given the IP address and name of the VM template.
Since we're running on the hypervisor, the IP address is localhost.

Where hypervisor-ip is replaced with the actual Hypervisor IP address.  While 
running Testpool on the hypervisor, use the tpl CLI to create a test pool::

  ./bin/tpl pool add example kvm qemu:///system test.template 3

Confirm the pool is valid::

  ./bin/tpl pool detail example

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
