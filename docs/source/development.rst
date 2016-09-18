.. _DevelopmentAnchor:

Debian Packaging
===============

Before debian packages can be created apt-file must be installed and updated
so that the python requirements.txt file can be mapped to equivalent 
debian package dependencies.

  sudo apt-get install apt-file
  sudo apt-file update
  pip install pep8>=1.7.0 pylint>=1.5.4 pytest>=2.8.3

Make sure to set EMAIL before using dch
Also note that versions are incremented in the change log
  dch -U
