.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Ubuntu 14.04
============

geni-lib is currently delivered only as a source repository via mercurial, although
dependencies are installed as proper packages using apt.

=======================
High-Level Dependencies
=======================

* Mercurial (http://mercurial.selenic.com)
* Python 2.7.x (http://www.python.org)
* M2Crypto
* Python Dateutil
* OpenSSL
* LibXML

The above packages of course have their own dependencies which will be satisfied along the way.

====================
Install Dependencies
====================

These instructions install depedencies using apt - it is also possible to install the Python packages
using pip if you prefer.

::

  $ apt-get install mercurial python-m2crypto python-dateutil python-lxml \
    libxmlsec1 xmlsec1 libxmlsec1-openssl python-setuptools python-openssl

============
Get geni-lib
============
::

  $ hg clone http://bitbucket.org/barnstorm/geni-lib

=======
Install
=======
::

  $ cd geni-lib
  $ hg update -C 0.9-DEV
  $ python setup.py install
