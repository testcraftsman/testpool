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


Testpool Installation
---------------------

Here are the required steps to setup the demo environment. You must first
start with an Ubuntu 16.04 system.

#. Install several requried packages:

  **sudo apt-get install python-pip python-yaml libmysqlclient-dev python-dev**
#. Install testpool from the github release area:

  **sudo pip install https://github.com/testpool/testpool/archive/v0.1-alpha.9.tar.gz**
#. Create local temporary database

  **tbd-manage migrate**
#. Validate proper configuration. confirm all checks pass.

   **tbd db check**

A Short Tour
------------

In order to track test results, basic product information and testplans
must be defined by using **tbd**.

Products must have one or more branches associated with them. Products
and branches are used to organize tests results. Lets create a product
named **product1** with a branch **branch1.1**.

  **tbd product add product1 branch1.1**

To see the effect of this command:

  **tbd product list**
 
Testplans define testsuites, their tests and key values pairs that organize
test results. Testplans can be associated with any number of products.
Let's create a testplan with several testsuites and tests.

  **tbd testplan add testsuite1**

  **tbd testplan add testsuite2**

When done adding testsuites, pack them which makes sure internal data 
structures are organized in a way to be efficient.

  **tbd testplan pack**

  **tbd testplan key add 0 OS ubuntu14.04**

  **tbd testplan key add 1 OS ubuntu14.04**

  **tbd testplan test add 0 test1.1**

  **tbd testplan test add 0 test1.2**

  **tbd testplan test add 1 test2.1**

  **tbd testplan test add 1 test2.2**


The previous testplan commands created a **default** testplan since a name
was not defined. Now lets associated the testplan with the product.

  **tbd product testplan add product1 branch1.1 default**

Lets see what this has done. 

  **tbd testplan list**

Summarizes two testsuites each with two tests. The order value, not previously
specified, governs the order in which this content will be displayed here 
and in the web site. Lets take a look a the web content. In another window, 
start a temporary web server:

  **tbd-manage runserver**

Now open a browser and keep it open. We'll refer back to it:

  **http://127.0.0.1:8000/testpool**

Testpool assumes that products and branches require a build. Its this build
information along with everything else we've specified that are necessary
for tracking test results.

To create a build with the id **100**:
  **tbd build add product1 branch1.1 100**

Save a test result:

  **tbd result set product1 branch1.1 100 testsuite1 test1.1 pass OS=ubuntu14.04**
