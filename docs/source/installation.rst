.. _InstallationAnchor:

Installation
************

Getting Testpool
================

Testpool is installed from source, download the latest from `GitHub <http://www.github.com/testcraftsman/testpool/releases>`_. This is also where we track issues and feature request.

What is Installed
=================

Testpool consists of:
  #. A database installed on an Ubuntu 16.04 system, which can also be a KVM 
     hypervisor
  #. testpool-client, another repo, is installed on every client

Actually the last item is optional in that the testpool-client provides an API above the server's 
REST API.  One could simply use the REST interface directly.

Testpool Server Installation on Ubuntu 16.04
--------------------------------------------

A single testpool server is required. It maintains VM pool requirements for each hypervisor. Here are the
steps to install a testpool's server:

  #. Download testpool from github release area, for example v0.1.0::

      wget https://github.com/testcraftsman/testpool/archive/v0.1.0.tar.gz
      tar -xf testpool-0.l.0.tar.gz

  #. Skip this step if you are installing Testpool on the KVM hypervisor, most likely these packages are already installed.
     
      sudo -H apt-get install -y libvirt-dev libxen-dev virtinst

  #. Install several required packages::

      cd testpool-0.1.0
      cat requirements.system | sudo xargs apt-get -y install
      sudo -H apt-file update
      sudo -H pip install --upgrade pip
      sudo -H pip install -qr requirements.txt

  #. Create debian packages,in  a shell run::

      make deb.build

  #. Install::

      sudo -H make install
