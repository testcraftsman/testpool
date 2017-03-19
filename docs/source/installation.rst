.. _InstallationAnchor:

Installation
************

Getting Testpool
================

If you want the latest code you'll need a `GitHub <http://www.github.com/>`_ account. This is also where we track issues and feature request. This code
is committed into <http://guthub.com/testcraftsman/testpool>.

What is Installed
=================

Testpool consists of:
  #. a KVM hypervisor 
  #. A test pool database installed on an Ubuntu 16.04 system, which can be on the 
     KVM hypervisor
  #. testpool client software installed on every client

Actually the last item is optional in that the client API is a thin
wrapper around the server's REST interface.  One could simply use the REST
interface on each client. For evaluation purposes a single system can be used to install both the server and client packages. Actual deployments would install the server on a single system and the client packages on each client system.


Testpool Server Installation on Ubuntu 16.04
--------------------------------------------

A single testpool server is required for store VM pool status. Here are the
steps for installing testpool's server:

#. Download testpool from github release area::

  wget https://github.com/testcraftsman/testpool/archive/v0.0.7.tar.gz
  tar -xf testpool-0.0.7.tar.gz

#. Install several required packages::

  cd testpool
  cat requirements.system | sudo xargs apt-get install
  sudo pip install -qr requirements.txt
  sudo pip install easydict
  sudo apt-file update

#. Install latest testbed which can be found at **https://github.com/testbed/testbed/releases**. For example:

  **sudo pip install https://github.com/testbed/testbed/archive/v0.0.7.tar.gz**

#. Add testbed configuration 

#. Copy example testbed configuration 

  **cd /usr/local/testbed**
  **cp examples/etc/mysql.cnf etc/mysql.cnf**

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
