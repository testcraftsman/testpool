.. _InstallationAnchor:

Installation
************

Getting Testpool
================

If you want the latest code you'll need a `GitHub <http://www.github.com/>`_ account. This is also where we track issues and feature request. 

What is Installed
=================

Testpool consists of a centralized server as well as an optional client 
installation. Optional in that the client python API is a thin layer around
the servers REST interace. One could simply use the REST interace on each 
client. For evaluation purposes a single system can be used to install both 
the server and client packages. Actual deployments would install the server
on a single system and the client packages on each client system.


Server Installation on Ubuntu 14.04
-----------------------------------

A single testpool server is required for store VM pool status. Here are the
steps for installing testpool's server:

#. Install several packages:

   **sudo apt-get install libvirt-python django-split-settings>=0.1.3 testpool**

#. Install latest testbed which can be found at **https://github.com/testbed/testbed/releases**. For example:

   **sudo pip install https://github.com/testbed/testbed/archive/v0.1-alpha.8.tar.gz**
#. Add testbed configuration 

   **sudo cp /usr/local/testbed/apache2/sites-available/testbed.conf /etc/apache2/sites-available/testbed.conf**
#. Enable testbed apache configuration,

   **sudo ln -s /etc/apache2/sites-available/testbed.conf /etc/apache2/sites-enabled/testbed.conf**
#. Restart the apache server,

   **sudo service apache2 restart**
#. Assuming the default user "testbed" with password "password", create this 
   user in mysql:

   **mysql -u root -p -e "CREATE USER 'testbed'@'%' IDENTIFIED BY 'password';"**

   **mysql -u root -p -e "GRANT ALL PRIVILEGES ON * . * TO 'testbed'@'%';"**

   **mysql -u root -p -e "FLUSH PRIVILEGES;"**

   Any user name and password can be used. This information simply needs to 
   be provided in the final step when mysql.cnf is created. By default,
   **testbed** and **password** credentials are assumed.
#. On the server, create the testbed database. Usually this is done with
   the root account:

   **mysql -u root -p -e "create database testbed;"**
#. To allow testbed clients access to the database, edit /etc/mysql/my.cnf. 
   Comment out both lines:

   **#bind-address   = 127.0.0.1**

   **#skip-networking**
#. Restart mysql:

   **sudo service mysql restart**
#. Copy example testbed configuration 

  **cd /usr/local/testbed**
  **cp examples/etc/mysql.cnf etc/mysql.cnf**
#. Edit testbed configuration **/usr/local/testbed/etc/mysql.cnf** and change
   the password which was set in step 7.
#. Populate testbed database.

   **/usr/local/bin/tbd-manage migrate**
#. Create admin account for testbed database not to be confused with the 
   mysql admin account. This is a user that had full edit access in the 
   testbed database. Run the following command and answer the promps

   **/usr/local/bin/tbd-manage migrate**
#. Validate proper configuration **tbd db check** to confirm all checks pass.

Client Installation on Ubuntu 14.04
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

  Set host to the IP address of the testbed server. The user and passowrd 
  properties should also be changed appropriately.
#. Validate proper configuration. confirm all checks pass.

   **tbd db check**
