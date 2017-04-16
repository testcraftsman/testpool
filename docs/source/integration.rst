.. _IntegrationAnchor:


Log Stash Support
*****************

Testpool provides a structured log of profile status that includes the 
number of available VMs for each profile. This information can be 
pushed to logstash and visualized with Kibana or Graphana. 

These instructions explain how to enable structured logging, push them
to Logstash using Filebeat.

ELK Installation
================

ELK stack 5.3 is required which natively supports JSON FileBeat output. There are numerous
sites to explain ELK installation e.g.
http://www.itzgeek.com/how-tos/linux/ubuntu-how-tos/setup-elk-stack-ubuntu-16-04.html
was used to test the following content.

Testpool Configuration
======================

Configure testpool to save profile status. Edit the YAML file::

  /etc/testpool/testpool.yml

Validate changes::
  
  tplcfgcheck /etc/testpool/testpool.yml

Uncomment tpldaemon.profile.log. The default value is **/var/log/testpool/profile.log**
and restart testpool daemon::

  sudo systemctl restart tpl-daemon

Configure Logstash to receive JSON structured content. An example configuration
file at **/etc/testpool/etc/logstash/conf.d/02-testpool-beat-input.conf**.::

  sudo cp /etc/testpool/etc/logstash/conf.d/02-testpool-beat-input.conf /etc/logstash/conf.d/02-testpool-beat-input.conf
  sudo systemctl restart logstash


The Logstash **02-testpool-beat-input.conf** content.

.. literalinclude:: ../../etc/logstash/conf.d/02-testpool-beat-input.conf

Configure Filebeat to push JSON content. An example is available at
**/etc/testpool/filebeat/filebeat.yml** and can be copied verbatim.::

  sudo cp /etc/testpool/filebeat/filebeat.yml /etc/filebeat/filebeat.yml
  sudo systemctl restart filebeat

The content below shows a sample Filebeat configuration.

.. literalinclude:: ../../etc/filebeat/filebeat.yml


Kibana 5.3
**********

A sample Kibana dashboard with supporting visualization can be imported into
Kibana. Content is available at:
**/etc/testpool/kibana/testpool.json**.
**/etc/testpool/kibana/testpool-dashboard.json**.

