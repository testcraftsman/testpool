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

  #. Download testpool from github release area::

      wget https://github.com/testcraftsman/testpool/archive/v0.1.0.tar.gz
      tar -xf testpool-0.l.0.tar.gz

  #. Install several required packages::

      cd testpool-0.1.0
      cat requirements.system | sudo xargs apt-get -y install
      sudo apt-file update
      sudo pip install -qr requirements.txt
      sudo pip install easydict
      sudo pip install django-pure-pagination==0.2.1
      sudo pip install django-split-settings==0.1.3

  #. Create debian packages,in  a shell run::

      make deb.build

  #. Install latest testbed which can be found at **https://github.com/testbed/testbed/releases**. For example:

    make install

  #. Add testbed configuration 
  
  #. Copy example testbed configuration 
  
    cd /usr/local/testbed**
    cp examples/etc/mysql.cnf etc/mysql.cnf

  #. Edit testbed configuration **/usr/local/testbed/etc/mysql.cnf** and change
     the password which was set in step 7.

  #. Populate testbed database.

     **/usr/local/bin/tbd-manage migrate**
  #. Create admin account for testbed database not to be confused with the 
     mysql admin account. This is a user that had full edit access in the 
     testbed database. Run the following command and answer the prompts
  
     **/usr/local/bin/tbd-manage migrate**

  #. Validate proper configuration **tbd db check** to confirm all checks pass.

Client Installation on Ubuntu 16.04
-----------------------------------

Here are the steps to setup testbed on a client running Ubuntu 14.04.
Versions are currently available through github.com on
https://github.com/testbed/testbed/releases. Please look through the 
release site to find the latest version. The example below uses an older
version:

#. Install several packages:

  **sudo apt-get install python-pip python-yaml libmysqlclient-dev python-dev**

#. Install testbed from the github release area:

  **sudo pip install https://github.com/testbed/testbed/archive/v0.1-alpha.8.tar.gz**

    #. Edit the file testbed configuration file:

  **/usr/local/testbed/etc/mysql.cnf**

  Set host to the IP address of the testbed server. The user and password 
  properties should also be changed appropriately.

#. Validate proper configuration. confirm all checks pass.

   **tbd db check**
