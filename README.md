# Model2Code converter

Convert an xWoT meta-model to executable python code.

# Installation

from a terminal launch

sudo python setup.py install

this will compile and install the project to the pyhton libraries (eg. /usr/local/lib/python2.7/dist-packages/XWoT_Model_Translator-1.1-py2.7.egg). Furthermore it will install three scripts in /usr/local/bin/:
* physical2virtualEntities
* model2Python
* model2WADL
The configuration and logging.conf are copied into /etc/Model2WADL/ but it is possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. .logging.conf) in the user home directory or a file with the same name in the current working directory.