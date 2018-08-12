.. _IntegrationAnchor:


Log Stash Support
*****************

Testpool provides a structured log of pool status that includes the number of
available VMs for each pool. This information can be pushed to logstash and
visualized with Kibana or Graphana. 

The following instructions explain how to enable structured logging and push
them to Logstash using Filebeat.

ELK Installation
================

ELK stack 5.5 is required which natively supports JSON FileBeat output. There
are numerous sites to explain ELK installation e.g.
http://www.itzgeek.com/how-tos/linux/ubuntu-how-tos/setup-elk-stack-ubuntu-16-04.html was used to test the following content.

Testpool Configuration
======================

Configure testpool to save pool status. Edit the YAML file::

  /etc/testpool/testpool.yml

Validate changes::
  
  tplcfgcheck /etc/testpool/testpool.yml

Uncomment tpldaemon.pool.log. The default value is **/var/log/testpool/pool.log** and restart testpool daemon::

  sudo systemctl restart tpl-daemon

Configure Logstash to receive JSON structured content. An example configuration
file at **/etc/testpool/etc/logstash/conf.d/02-testpool-beat-input.conf**.::

  sudo cp /etc/testpool/etc/logstash/conf.d/02-testpool-beat-input.conf /etc/logstash/conf.d/02-testpool-beat-input.conf
  sudo systemctl restart logstash


Make sure elastic search and logstash start on boot:

  sudo systemctl enable logstash
  sudo systemctl enable elasticsearch


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
